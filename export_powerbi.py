# -*- coding: utf-8 -*-
"""
export_powerbi.py
Exports clean, Power BI–ready CSV tables into the powerbi/ folder.

There is no Python library that renders data *inside* Power BI without a Power
BI account/service (a live link needs the Power BI REST API + a workspace + a
sign-in). The practical, account-free path is to import clean CSVs into Power
BI Desktop — which is what this produces.

Files are written UTF-8 with BOM (utf-8-sig) so Arabic text imports correctly
in Power BI / Excel. Run:

    python export_powerbi.py
"""
import os

import pandas as pd

from analysis import (load_data, build_baseline, detect_anomalies, summarize,
                      project_future_cost)
from real_analysis import build_regional_table, national_loss_scenarios

OUT = "powerbi"


def _write(df, name):
    df.to_csv(os.path.join(OUT, name), index=False, encoding="utf-8-sig")
    print(f"  {OUT}/{name}  ({len(df)} rows, {len(df.columns)} cols)")


def main():
    os.makedirs(OUT, exist_ok=True)

    # ---- Leak-detection engine (fact + dimension tables) ----
    scored = detect_anomalies(build_baseline(load_data()))

    fact = scored.rename(columns={
        "zone_id": "site_id",
        "zone_name": "site",
        "consumption_m3": "consumption_m3",
        "baseline_m3": "expected_baseline_m3",
        "residual_m3": "residual_m3",
        "z_score": "z_score",
        "pct_over_baseline": "pct_over_baseline",
        "predicted_leak": "is_leak_detected",
        "is_actual_leak_period": "is_actual_leak",
        "excess_m3": "excess_m3",
        "financial_loss_sar": "financial_loss_sar",
        "tariff_sar_per_m3": "tariff_sar_per_m3",
    })[[
        "date", "site_id", "site", "tariff_sar_per_m3", "consumption_m3",
        "expected_baseline_m3", "residual_m3", "z_score", "pct_over_baseline",
        "is_leak_detected", "excess_m3", "financial_loss_sar", "is_actual_leak",
    ]].copy()
    _num = fact.select_dtypes("number").columns
    fact[_num] = fact[_num].round(3)
    _write(fact, "meter_readings_scored.csv")

    summary = summarize(scored).round(2)
    proj = {zid: project_future_cost(scored, zid, 30) for zid in scored["zone_id"].unique()}
    name_by_id = scored.groupby("zone_id")["zone_name"].first().to_dict()
    proj_rows = [{
        "site_id": zid,
        "site": name_by_id[zid],
        "active_leak": p["currently_active_leak"],
        "avg_daily_excess_m3": p["avg_daily_excess_m3"],
        "projected_30d_loss_sar": p["projected_loss_next_30_days_sar"],
    } for zid, p in proj.items()]
    _write(summary, "site_loss_summary.csv")
    _write(pd.DataFrame(proj_rows), "site_projection_30d.csv")

    # ---- National gap (published real data) ----
    _write(build_regional_table(), "regional_gap.csv")
    _write(national_loss_scenarios(), "national_loss_scenarios.csv")

    # ---- Short import guide ----
    guide = (
        "# استيراد البيانات في Power BI  |  Import into Power BI\n\n"
        "## بالعربي\n"
        "1. افتح Power BI Desktop.\n"
        "2. Home → Get Data → Text/CSV.\n"
        "3. اختر أي ملف من هذا المجلد (`powerbi/`)، مثلاً `meter_readings_scored.csv`، ثم Load.\n"
        "4. كرّر لبقية الملفات. الملفات مرمّزة UTF-8 فالعربي يظهر سليمًا.\n"
        "5. أنشئ العلاقات: اربط `site_id` بين الجداول (Model view).\n"
        "6. أمثلة مقاييس (Measures / DAX):\n"
        "   - إجمالي الخسارة:  Total Loss = SUM(meter_readings_scored[financial_loss_sar])\n"
        "   - أيام التسرب:      Leak Days  = CALCULATE(COUNTROWS(meter_readings_scored), meter_readings_scored[is_leak_detected] = TRUE())\n"
        "   - الخسارة المتوقعة 30 يوم:  Proj 30d = SUM(site_projection_30d[projected_30d_loss_sar])\n\n"
        "## English\n"
        "1. Power BI Desktop → Home → Get Data → Text/CSV.\n"
        "2. Load each file in this folder; files are UTF-8 so Arabic imports correctly.\n"
        "3. In Model view, relate the tables on `site_id`.\n"
        "4. Build visuals from the measures above (Total Loss, Leak Days, Proj 30d).\n\n"
        "Files:\n"
        "- meter_readings_scored.csv   — fact table: one row per site per day, with baseline, detection flags and SAR loss\n"
        "- site_loss_summary.csv       — per-site totals\n"
        "- site_projection_30d.csv     — per-site 30-day projection + active-leak flag\n"
        "- regional_gap.csv            — national consumption gap vs the 2030 target (real published data)\n"
        "- national_loss_scenarios.csv — national network-loss value by tariff tier\n"
    )
    with open(os.path.join(OUT, "HOW_TO_IMPORT.md"), "w", encoding="utf-8") as f:
        f.write(guide)
    print(f"  {OUT}/HOW_TO_IMPORT.md")


if __name__ == "__main__":
    print("Exporting Power BI CSVs...")
    main()
    print("Done.")
