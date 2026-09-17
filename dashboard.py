"""
dashboard.py
On-premise financial-impact dashboard for water loss detection.

Designed to run as a local Streamlit server inside the company network
(e.g. alongside a Saudi Meters AMI historian or a WETICO SCADA server),
with zero outbound cloud dependency: all data stays on local disk / an
internal database connection you can swap in later (see README).

Bilingual: Arabic (RTL) / English (LTR), switchable at runtime via the
language selector in the header (see i18n.py).
"""
import pandas as pd
import streamlit as st
import plotly.express as px

from analysis import load_data, build_baseline, detect_anomalies, summarize, project_future_cost
from i18n import SIM, language_selector, apply_direction, zone_label

# Language must be resolved before the first Streamlit call so the page
# title and text direction are correct for this run.
lang = st.session_state.get("lang", "ar")
tr = SIM[lang]

st.set_page_config(page_title=tr["page_title"], layout="wide", page_icon="💧")

st.markdown(
    """
    <style>
    .kpi-card {background-color:#f5f7fa; border-radius:10px; padding:18px; text-align:center; border:1px solid #e3e6ea;}
    .kpi-value {font-size:28px; font-weight:700; color:#0b3d5c;}
    .kpi-label {font-size:13px; color:#5a6a7a;}
    </style>
    """,
    unsafe_allow_html=True,
)

apply_direction(lang)
language_selector()

st.title(tr["title"])
st.caption(tr["caption"])

raw = load_data()
scored = detect_anomalies(build_baseline(raw))
summary = summarize(scored)

total_loss = summary["total_financial_loss_sar"].sum()
total_excess = summary["total_excess_m3"].sum()
total_leak_days = int(summary["leak_days_detected"].sum())
zones_at_risk = int((summary["total_financial_loss_sar"] > 0).sum())
# Aggregate 30-day projection across every currently-active leak.
proj_total_30d = sum(
    project_future_cost(scored, zid, 30)["projected_loss_next_30_days_sar"]
    for zid in scored["zone_id"].unique()
)

c1, c2, c3, c4, c5 = st.columns(5)
for col, label, value in zip(
    [c1, c2, c3, c4, c5],
    [tr["kpi_loss"], tr["kpi_days"], tr["kpi_proj30"], tr["kpi_excess"], tr["kpi_zones"]],
    [f"{total_loss:,.0f}", f"{total_leak_days:,}", f"{proj_total_30d:,.0f}", f"{total_excess:,.0f}", f"{zones_at_risk}"],
):
    col.markdown(
        f'<div class="kpi-card"><div class="kpi-value">{value}</div><div class="kpi-label">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.divider()

left, right = st.columns([2, 1])

with left:
    st.subheader(tr["sec_consumption"])
    zone_options = scored["zone_name"].unique().tolist()
    selected_zone = st.selectbox(
        tr["select_zone"], zone_options, format_func=lambda z: zone_label(z, lang)
    )
    zdf = scored[scored["zone_name"] == selected_zone].sort_values("date")

    fig = px.line(
        zdf, x="date", y=["consumption_m3", "baseline_m3"],
        labels={"value": tr["axis_m3"], "date": tr["axis_date"], "variable": ""},
        color_discrete_map={"consumption_m3": "#e74c3c", "baseline_m3": "#2c7fb8"},
    )
    # Give the two series human, translated legend names.
    series_names = {
        "consumption_m3": tr["series_consumption"],
        "baseline_m3": tr["series_baseline"],
    }
    fig.for_each_trace(lambda t: t.update(name=series_names.get(t.name, t.name)))

    leak_points = zdf[zdf["predicted_leak"]]
    fig.add_scatter(
        x=leak_points["date"], y=leak_points["consumption_m3"],
        mode="markers", marker=dict(color="black", size=5, symbol="x"),
        name=tr["series_leak"],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(tr["sec_daily_impact"])
    fig2 = px.bar(zdf, x="date", y="financial_loss_sar", labels={"financial_loss_sar": tr["axis_sar"], "date": ""})
    fig2.update_traces(marker_color="#c0392b")
    st.plotly_chart(fig2, use_container_width=True)

with right:
    st.subheader(tr["sec_summary"])
    summary_display = summary.copy()
    summary_display["zone_name"] = summary_display["zone_name"].map(lambda z: zone_label(z, lang))
    st.dataframe(
        summary_display.rename(columns={
            "zone_name": tr["col_zone"],
            "total_consumption_m3": tr["col_total_consumption"],
            "leak_days_detected": tr["col_leak_days"],
            "total_excess_m3": tr["col_excess"],
            "total_financial_loss_sar": tr["col_loss"],
        }),
        hide_index=True,
        use_container_width=True,
    )

    st.subheader(tr["sec_projection"])
    zone_id_map = dict(zip(scored["zone_name"], scored["zone_id"]))
    for zname, zid in zone_id_map.items():
        proj = project_future_cost(scored, zid, forward_days=30)
        display_name = zone_label(zname, lang)
        if proj["currently_active_leak"]:
            amount = f"{proj['projected_loss_next_30_days_sar']:,.0f}"
            st.error(tr["proj_active"].format(zone=display_name, amount=amount))
        else:
            st.success(tr["proj_ok"].format(zone=display_name))

st.divider()
st.caption(tr["footer"])
