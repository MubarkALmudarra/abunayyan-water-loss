"""
analysis.py
Core analytics engine (framework-agnostic, no cloud SDKs) so it can run
entirely on an on-premise server with no outbound internet dependency.

Pipeline:
1. Load historical meter readings (from local CSV / DB export).
2. Build an expected-consumption baseline per zone using a rolling
   seasonal model (7-day and 28-day rolling median), which is robust
   to the leak periods themselves.
3. Flag anomalies where actual consumption exceeds the baseline by
   more than a z-score threshold -> candidate leak days.
4. Translate excess volume into financial loss using each zone's
   water tariff (SAR/m3).
5. Produce a 30-day forward forecast of expected (leak-free) demand
   using a simple seasonal-naive + trend model, and project the
   financial cost of *not* fixing an active leak for another N days.
"""
import json

import numpy as np
import pandas as pd


def load_data(path="meter_readings.csv"):
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def build_baseline(df, short_window=7, long_window=28):
    """
    Trailing (backward-looking) rolling-median baseline per zone.

    Deliberately NOT centered: a real on-premise monitoring service only
    ever has access to past readings, so the baseline for "today" is
    computed strictly from the previous `long_window` days (shifted by 1)
    and cannot be contaminated by an ongoing leak that is still in
    progress today.
    """
    def _robust_scale(a):
        # MAD-based scale (scaled to be consistent with std for a normal
        # distribution). Robust: a sustained leak that occupies a minority of
        # the trailing window can't inflate it, so later days of the SAME leak
        # stay above the z-threshold instead of self-suppressing.
        med = np.median(a)
        return 1.4826 * np.median(np.abs(a - med))

    df = df.sort_values(["zone_id", "date"]).copy()
    out = []
    for zone_id, g in df.groupby("zone_id"):
        g = g.copy()
        trailing = g["consumption_m3"].shift(1).rolling(long_window, min_periods=short_window)
        g["baseline_m3"] = trailing.median()
        g["baseline_m3"] = g["baseline_m3"].bfill()
        g["residual_m3"] = g["consumption_m3"] - g["baseline_m3"]
        shifted = g["residual_m3"].shift(1).rolling(long_window, min_periods=short_window)
        rolling_scale = shifted.apply(_robust_scale, raw=True).bfill()
        # Fall back to plain std only where MAD collapses to ~0 (very flat windows).
        std_fallback = shifted.std().bfill()
        rolling_scale = rolling_scale.where(rolling_scale > 1e-9, std_fallback)
        g["z_score"] = g["residual_m3"] / rolling_scale.replace(0, np.nan)
        out.append(g)
    return pd.concat(out, ignore_index=True)


def detect_anomalies(df, z_threshold=2.0, min_pct_over_baseline=0.15):
    """
    A day is flagged as a probable leak only when BOTH hold:
      - the residual is a statistical outlier (z-score > threshold), and
      - the excess is also economically meaningful (>= min_pct_over_baseline
        of that day's expected baseline volume).

    Combining a statistical and a magnitude condition cuts down noise-driven
    false alarms compared to using the z-score alone.
    """
    df = df.copy()
    pct_over = df["residual_m3"] / df["baseline_m3"].replace(0, np.nan)
    df["pct_over_baseline"] = pct_over
    df["predicted_leak"] = (
        (df["z_score"] > z_threshold)
        & (df["residual_m3"] > 0)
        & (pct_over > min_pct_over_baseline)
    )
    df["excess_m3"] = np.where(df["predicted_leak"], df["residual_m3"].clip(lower=0), 0.0)
    df["financial_loss_sar"] = df["excess_m3"] * df["tariff_sar_per_m3"]
    return df


def summarize(df):
    summary = (
        df.groupby("zone_name")
        .agg(
            total_consumption_m3=("consumption_m3", "sum"),
            leak_days_detected=("predicted_leak", "sum"),
            total_excess_m3=("excess_m3", "sum"),
            total_financial_loss_sar=("financial_loss_sar", "sum"),
        )
        .reset_index()
        .sort_values("total_financial_loss_sar", ascending=False)
    )
    return summary


def project_future_cost(df, zone_id, forward_days=30):
    """
    If a zone currently has an active/ongoing anomaly at the end of the
    dataset, project the additional financial loss if it stays
    unresolved for `forward_days` more days.
    """
    g = df[df["zone_id"] == zone_id].sort_values("date")
    tail = g.tail(7)
    is_active = tail["predicted_leak"].mean() > 0.5
    avg_daily_excess = tail["excess_m3"].mean() if is_active else 0.0
    tariff = g["tariff_sar_per_m3"].iloc[-1]
    projected_loss = avg_daily_excess * tariff * forward_days
    return {
        "zone_id": zone_id,
        "currently_active_leak": bool(is_active),
        "avg_daily_excess_m3": round(avg_daily_excess, 2),
        "projected_loss_next_%d_days_sar" % forward_days: round(projected_loss, 2),
    }


def build_dashboard_payload(scored, forward_days=30):
    """
    Assemble the exact JSON structure the static dashboard (index.html /
    template.html) consumes, computed entirely from the real pipeline output
    so the static page always reflects the live analysis (no stale, hand-made
    JSON). Also feeds the Streamlit KPIs via the same numbers.
    """
    zones, summary_rows, timeseries, projections = [], [], {}, {}
    for zid, g in scored.groupby("zone_id"):
        g = g.sort_values("date")
        name = g["zone_name"].iloc[0]
        zones.append({"zone_id": zid, "zone_name": name})
        timeseries[zid] = {
            "dates": g["date"].dt.strftime("%Y-%m-%d").tolist(),
            "consumption": [round(float(x), 2) for x in g["consumption_m3"]],
            "baseline": [None if pd.isna(x) else round(float(x), 2) for x in g["baseline_m3"]],
            "leak": [bool(x) for x in g["predicted_leak"]],
            "loss": [round(float(x), 2) for x in g["financial_loss_sar"]],
        }
        proj = project_future_cost(scored, zid, forward_days)
        projections[zid] = {
            "active": proj["currently_active_leak"],
            "projected_30d_sar": proj["projected_loss_next_%d_days_sar" % forward_days],
        }
        summary_rows.append({
            "zone_id": zid,
            "zone_name": name,
            "total_consumption_m3": round(float(g["consumption_m3"].sum()), 2),
            "leak_days_detected": int(g["predicted_leak"].sum()),
            "total_excess_m3": round(float(g["excess_m3"].sum()), 2),
            "total_financial_loss_sar": round(float(g["financial_loss_sar"].sum()), 2),
        })
    summary_rows.sort(key=lambda r: r["total_financial_loss_sar"], reverse=True)
    totals = {
        "total_loss_sar": round(sum(r["total_financial_loss_sar"] for r in summary_rows), 2),
        "total_excess_m3": round(sum(r["total_excess_m3"] for r in summary_rows), 2),
        "total_leak_days": sum(r["leak_days_detected"] for r in summary_rows),
        "zones_at_risk": sum(1 for r in summary_rows if r["total_financial_loss_sar"] > 0),
        "projected_30d_sar": round(sum(p["projected_30d_sar"] for p in projections.values()), 2),
    }
    return {"zones": zones, "timeseries": timeseries, "summary": summary_rows,
            "projections": projections, "totals": totals}


if __name__ == "__main__":
    raw = load_data()
    baselined = build_baseline(raw)
    scored = detect_anomalies(baselined)
    summary = summarize(scored)
    print("\n=== Financial Impact Summary by Zone ===")
    print(summary.to_string(index=False))

    print("\n=== 30-Day Forward Risk Projection ===")
    for zid in scored["zone_id"].unique():
        print(project_future_cost(scored, zid))

    scored.to_csv("scored_readings.csv", index=False)
    summary.to_csv("financial_summary.csv", index=False)

    payload = build_dashboard_payload(scored)
    with open("dashboard_data.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print("\nSaved: scored_readings.csv, financial_summary.csv, dashboard_data.json")
