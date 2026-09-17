# -*- coding: utf-8 -*-
"""
لوحة Streamlit مبنية بالكامل على بيانات حقيقية منشورة (real_data.py / real_analysis.py).
لا يوجد أي توليد عشوائي هنا. شغّلها بـ: streamlit run real_dashboard.py

Bilingual dashboard built entirely on published real data.
Arabic (RTL) / English (LTR) switchable at runtime — see i18n.py.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from real_analysis import build_regional_table, national_loss_scenarios
from real_data import (
    SOURCES, VISION2030_TARGET_LPCD,
    NATIONAL_DAILY_LOSS_M3_LOW, NATIONAL_DAILY_LOSS_M3_HIGH,
)
from i18n import (
    REAL, language_selector, apply_direction,
    region_label, note_label, tier_label,
)

# Resolve language before the first Streamlit call.
lang = st.session_state.get("lang", "ar")
tr = REAL[lang]

st.set_page_config(page_title=tr["page_title"], layout="wide")

apply_direction(lang)
language_selector()

st.title(tr["title"])
st.caption(tr["caption"])

reg_df = build_regional_table()
nat_df = national_loss_scenarios()

total_excess_m3 = int(reg_df["excess_m3_per_year"].sum())
total_value_low = int(reg_df["excess_value_sar_low_tariff"].sum())
total_value_high = int(reg_df["excess_value_sar_high_tariff"].sum())

conf_true, conf_false = tr["confirmed_true"], tr["confirmed_false"]

c1, c2, c3 = st.columns(3)
c1.metric(tr["kpi_excess"], f"{total_excess_m3:,} {tr['kpi_excess_unit']}")
c2.metric(tr["kpi_value"], f"{total_value_low:,} — {total_value_high:,} {tr['kpi_value_unit']}")
c3.metric(tr["kpi_national"], f"{NATIONAL_DAILY_LOSS_M3_LOW:,} — {NATIONAL_DAILY_LOSS_M3_HIGH:,} {tr['kpi_national_unit']}")

st.warning(tr["warning"])

# ---- 1. Per-capita consumption by region vs. 2030 target ----
st.subheader(tr["sec_lpcd"])
plot_df = reg_df.sort_values("lpcd_2022", ascending=False).copy()
plot_df["region_disp"] = plot_df["region"].map(lambda r: region_label(r, lang))
plot_df["conf_disp"] = plot_df["data_confirmed"].map(lambda b: conf_true if b else conf_false)
fig = px.bar(
    plot_df, x="region_disp", y="lpcd_2022", color="conf_disp",
    color_discrete_map={conf_true: "#0E7C7B", conf_false: "#9AA39C"},
    labels={"region_disp": tr["axis_region"], "lpcd_2022": tr["axis_lpcd"], "conf_disp": tr["legend_confirmed"]},
    category_orders={"region_disp": plot_df["region_disp"].tolist()},
)
fig.add_hline(y=VISION2030_TARGET_LPCD, line_dash="dash", line_color="#B23A3A",
              annotation_text=tr["target_line"])
st.plotly_chart(fig, use_container_width=True)

# ---- 2. Economic-gap table by region ----
st.subheader(tr["sec_table"])
table_df = reg_df.copy()
table_df["region"] = table_df["region"].map(lambda r: region_label(r, lang))
table_df["note"] = table_df["note"].map(lambda n: note_label(n, lang))
table_df["data_confirmed"] = table_df["data_confirmed"].map(lambda b: conf_true if b else conf_false)
show_cols = ["region", "population_2022", "lpcd_2022", "data_confirmed", "note",
             "excess_lpcd_vs_2030_target", "excess_m3_per_year",
             "excess_value_sar_low_tariff", "excess_value_sar_high_tariff"]
table_df = table_df[show_cols].rename(columns={
    "region": tr["col_region"],
    "population_2022": tr["col_population"],
    "lpcd_2022": tr["col_lpcd"],
    "data_confirmed": tr["col_confirmed"],
    "note": tr["col_note"],
    "excess_lpcd_vs_2030_target": tr["col_excess_lpcd"],
    "excess_m3_per_year": tr["col_excess_m3"],
    "excess_value_sar_low_tariff": tr["col_value_low"],
    "excess_value_sar_high_tariff": tr["col_value_high"],
})
st.dataframe(table_df, use_container_width=True, hide_index=True)

# ---- 3. Sensitivity of national network-loss value by tariff tier ----
st.subheader(tr["sec_sensitivity"])
# Use stable keys ("low"/"high") for the control and filter on the numeric
# daily-loss value, so the filter never depends on a translated label string.
choice = st.radio(
    tr["radio_label"], options=["low", "high"], horizontal=True,
    format_func=lambda k: tr["scenario_low"] if k == "low" else tr["scenario_high"],
)
daily = NATIONAL_DAILY_LOSS_M3_LOW if choice == "low" else NATIONAL_DAILY_LOSS_M3_HIGH
sub = nat_df[nat_df["daily_loss_m3"] == daily].copy()
sub["tier_disp"] = sub["tariff_tier"].map(lambda t: tier_label(t, lang))
fig2 = px.bar(
    sub, x="tier_disp", y="illustrative_annual_value_sar",
    labels={"tier_disp": tr["axis_tier"], "illustrative_annual_value_sar": tr["axis_annual_value"]},
    category_orders={"tier_disp": sub["tier_disp"].tolist()},
)
st.plotly_chart(fig2, use_container_width=True)

# ---- Sources (citations kept as published) ----
st.subheader(tr["sec_sources"])
for s in SOURCES.values():
    st.markdown(f"- [{s['title']}]({s['url']})")
