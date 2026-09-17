# -*- coding: utf-8 -*-
"""
تحليل حقيقي 100% مبني على أرقام منشورة فعليًا (انظر real_data.py للمصادر).
لا يوجد أي توليد عشوائي أو بيانات مصطنعة في هذا الملف.
"""
import json
import pandas as pd
from real_data import (
    POPULATION_2022, CONSUMPTION_LPCD, VISION2030_TARGET_LPCD,
    TARIFF_TIERS, LOWEST_TARIFF, HIGHEST_TARIFF,
    NATIONAL_DAILY_LOSS_M3_LOW, NATIONAL_DAILY_LOSS_M3_HIGH,
    NATIONAL_AVG_LPCD_2022, NATIONAL_AVG_LPCD_2010, SOURCES,
)

def build_regional_table():
    rows = []
    for region, pop in POPULATION_2022.items():
        lpcd, confirmed, note = CONSUMPTION_LPCD[region]
        excess_lpcd = max(0.0, lpcd - VISION2030_TARGET_LPCD)
        excess_m3_per_year = (excess_lpcd / 1000.0) * pop * 365.0
        value_low = excess_m3_per_year * LOWEST_TARIFF
        value_high = excess_m3_per_year * HIGHEST_TARIFF
        rows.append({
            "region": region,
            "population_2022": pop,
            "lpcd_2022": lpcd,
            "data_confirmed": confirmed,
            "note": note,
            "excess_lpcd_vs_2030_target": round(excess_lpcd, 1),
            "excess_m3_per_year": round(excess_m3_per_year),
            "excess_value_sar_low_tariff": round(value_low),
            "excess_value_sar_high_tariff": round(value_high),
        })
    df = pd.DataFrame(rows).sort_values("lpcd_2022", ascending=False).reset_index(drop=True)
    return df

def national_loss_scenarios():
    scenarios = []
    for daily_m3, label in [(NATIONAL_DAILY_LOSS_M3_LOW, "الحد الأدنى المنشور (600 ألف م³/يوم)"),
                             (NATIONAL_DAILY_LOSS_M3_HIGH, "الحد الأعلى المنشور (800 ألف م³/يوم)")]:
        annual_m3 = daily_m3 * 365
        for tier in TARIFF_TIERS:
            scenarios.append({
                "loss_scenario": label,
                "daily_loss_m3": daily_m3,
                "annual_loss_m3": annual_m3,
                "tariff_tier": tier["tier"],
                "tariff_rate": tier["rate_sar_per_m3"],
                "illustrative_annual_value_sar": round(annual_m3 * tier["rate_sar_per_m3"]),
            })
    return pd.DataFrame(scenarios)

def main():
    reg_df = build_regional_table()
    nat_df = national_loss_scenarios()

    reg_df.to_csv("real_regional_analysis.csv", index=False, encoding="utf-8-sig")
    nat_df.to_csv("real_national_loss_scenarios.csv", index=False, encoding="utf-8-sig")

    total_excess_value_low = int(reg_df["excess_value_sar_low_tariff"].sum())
    total_excess_value_high = int(reg_df["excess_value_sar_high_tariff"].sum())
    total_excess_m3 = int(reg_df["excess_m3_per_year"].sum())

    payload = {
        "sources": SOURCES,
        "national_avg_lpcd_2022": NATIONAL_AVG_LPCD_2022,
        "national_avg_lpcd_2010": NATIONAL_AVG_LPCD_2010,
        "vision2030_target_lpcd": VISION2030_TARGET_LPCD,
        "tariff_tiers": TARIFF_TIERS,
        "national_loss_low_m3_day": NATIONAL_DAILY_LOSS_M3_LOW,
        "national_loss_high_m3_day": NATIONAL_DAILY_LOSS_M3_HIGH,
        "regional": json.loads(reg_df.to_json(orient="records", force_ascii=False)),
        "national_scenarios": json.loads(nat_df.to_json(orient="records", force_ascii=False)),
        "totals": {
            "total_excess_m3_per_year": total_excess_m3,
            "total_excess_value_sar_low_tariff": total_excess_value_low,
            "total_excess_value_sar_high_tariff": total_excess_value_high,
        },
    }
    with open("real_dashboard_data.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("=== جدول المناطق ===")
    print(reg_df[["region","population_2022","lpcd_2022","data_confirmed","excess_lpcd_vs_2030_target","excess_m3_per_year"]].to_string(index=False))
    print("\n=== إجمالي القيمة الاقتصادية التوضيحية لفجوة الاستهلاك عن هدف 2030 (وطنيًا) ===")
    print(f"الحجم الزائد: {total_excess_m3:,} م³/سنة")
    print(f"القيمة عند أدنى تعرفة (0.15 ريال/م³): {total_excess_value_low:,} ريال/سنة")
    print(f"القيمة عند أعلى تعرفة (9.00 ريال/م³): {total_excess_value_high:,} ريال/سنة")
    print("\n=== سيناريوهات فاقد الشبكة الوطني (600-800 ألف م³/يوم) ===")
    print(nat_df.to_string(index=False))

if __name__ == "__main__":
    main()
