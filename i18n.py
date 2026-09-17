# -*- coding: utf-8 -*-
"""
i18n.py
Shared bilingual (Arabic / English) support for the Streamlit dashboards.

Provides:
  - language_selector(): renders a small AR/EN switcher and returns the
    active language code ("ar" or "en"), persisted in st.session_state.
  - apply_direction(lang): injects CSS so the whole interface flips to
    RTL for Arabic and LTR for English (layout/branding unchanged).
  - SIM / REAL: translation dictionaries for the two dashboards.
  - Name maps for zones (English data -> Arabic) and regions
    (Arabic data -> English) so data-derived labels are bilingual too.

No cloud dependency — pure Python + Streamlit, on-premise friendly.
"""
import streamlit as st

LANG_LABELS = {"ar": "العربية", "en": "English"}
DEFAULT_LANG = "ar"


def get_lang() -> str:
    """Return the active language code, defaulting to Arabic."""
    return st.session_state.get("lang", DEFAULT_LANG)


def language_selector() -> str:
    """
    Render the language switcher (top of the page) and return the active
    language code. Changing it triggers Streamlit's normal rerun, so the
    whole interface re-renders in the chosen language.
    """
    if "lang" not in st.session_state:
        st.session_state["lang"] = DEFAULT_LANG

    # Push the switcher to the trailing edge of the header row.
    spacer, box = st.columns([5, 1])
    with box:
        st.radio(
            "Language / اللغة",
            options=["ar", "en"],
            key="lang",
            horizontal=True,
            format_func=lambda code: LANG_LABELS[code],
            label_visibility="collapsed",
        )
    return st.session_state["lang"]


def apply_direction(lang: str) -> None:
    """
    Inject direction-aware CSS. Arabic => RTL, English => LTR.
    Targets the Streamlit app containers so text alignment and the
    column/flex order follow the active language.
    """
    if lang == "ar":
        direction, text_align = "rtl", "right"
    else:
        direction, text_align = "ltr", "left"

    st.markdown(
        f"""
        <style>
        html {{ direction: {direction}; }}
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
            direction: {direction};
            text-align: {text_align};
        }}
        /* Keep the language switcher itself horizontal and readable. */
        [data-testid="stRadio"] > div {{ flex-direction: row; }}
        /* Streamlit metrics + dataframes read better aligned to the flow. */
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
            text-align: {text_align};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Translations for dashboard.py  (simulated meter-level leak detection)
# --------------------------------------------------------------------------
SIM = {
    "ar": {
        "page_title": "الأثر المالي لفاقد المياه | أبونيان",
        "title": "💧 نظام تحليل الخسائر المالية الناتجة عن تسربات المياه",
        "caption": "محرك الأثر المالي (On-premise) — يعمل بالكامل على سيرفرات الشركة الداخلية دون الاعتماد على أي خدمة سحابية خارجية",
        "kpi_loss": "إجمالي الخسائر المالية (ريال)",
        "kpi_excess": "إجمالي المياه المهدرة (م³)",
        "kpi_days": "أيام التسرب المكتشفة",
        "kpi_proj30": "الخسارة المتوقعة خلال 30 يوم (ريال)",
        "kpi_zones": "عدد المواقع المتأثرة",
        "sec_consumption": "الاستهلاك الفعلي مقابل الأساس المتوقع (Baseline)",
        "select_zone": "اختر الموقع",
        "series_consumption": "الاستهلاك الفعلي",
        "series_baseline": "الأساس المتوقع",
        "series_leak": "تسرب مكتشف",
        "axis_date": "التاريخ",
        "axis_m3": "م³",
        "axis_sar": "ريال",
        "sec_daily_impact": "الأثر المالي اليومي (ريال) لهذا الموقع",
        "sec_summary": "ملخص الخسائر حسب الموقع",
        "col_zone": "الموقع",
        "col_total_consumption": "إجمالي الاستهلاك (م³)",
        "col_leak_days": "أيام التسرب",
        "col_excess": "الفاقد (م³)",
        "col_loss": "الخسارة (ريال)",
        "sec_projection": "توقع الخسارة خلال 30 يوم القادمة إذا لم يُعالج التسرب",
        "proj_active": "⚠️ **{zone}**: تسرب نشط حالياً — خسارة متوقعة إضافية **{amount} ريال** خلال 30 يوم إذا لم يُعالج.",
        "proj_ok": "✅ **{zone}**: لا يوجد تسرب نشط حالياً.",
        "footer": (
            "المنهجية: خط أساس متحرك (Rolling Median) مقاوم للتطرفات + كشف شذوذ بمعيار Z-score، "
            "محوّل مباشرة لتكلفة مالية عبر تعرفة المياه لكل موقع. الكود بالكامل بلا أي استدعاء إنترنت خارجي — "
            "قابل للتشغيل كخدمة داخلية على سيرفر الشركة (Docker / systemd service)."
        ),
    },
    "en": {
        "page_title": "Water Loss Financial Impact | Abunayyan",
        "title": "💧 Water Loss Financial Impact Engine",
        "caption": "On-premise Financial Impact Engine — runs entirely on the company's internal servers with no external cloud dependency.",
        "kpi_loss": "Total financial loss (SAR)",
        "kpi_excess": "Total water wasted (m³)",
        "kpi_days": "Leak days detected",
        "kpi_proj30": "Projected 30-day loss (SAR)",
        "kpi_zones": "Affected sites",
        "sec_consumption": "Actual consumption vs. expected baseline",
        "select_zone": "Select a site",
        "series_consumption": "Actual consumption",
        "series_baseline": "Expected baseline",
        "series_leak": "Detected leak",
        "axis_date": "Date",
        "axis_m3": "m³",
        "axis_sar": "SAR",
        "sec_daily_impact": "Daily financial impact (SAR) for this site",
        "sec_summary": "Loss summary by site",
        "col_zone": "Site",
        "col_total_consumption": "Total consumption (m³)",
        "col_leak_days": "Leak days",
        "col_excess": "Water lost (m³)",
        "col_loss": "Loss (SAR)",
        "sec_projection": "Projected loss over the next 30 days if the leak is left untreated",
        "proj_active": "⚠️ **{zone}**: leak currently active — projected additional loss of **{amount} SAR** over 30 days if left untreated.",
        "proj_ok": "✅ **{zone}**: no active leak right now.",
        "footer": (
            "Methodology: an outlier-robust trailing Rolling-Median baseline + Z-score anomaly detection, "
            "converted directly into a financial cost via each site's water tariff. The entire codebase makes no "
            "external internet calls — it can run as an internal service on the company's own server (Docker / systemd)."
        ),
    },
}

# Zone names are stored in the data in English; map them to Arabic display.
ZONE_NAMES = {
    "Industrial Plant - Riyadh": {"ar": "مصنع صناعي — الرياض", "en": "Industrial Plant - Riyadh"},
    "Commercial Complex - Dammam": {"ar": "مجمع تجاري — الدمام", "en": "Commercial Complex - Dammam"},
    "Residential Compound - Jeddah": {"ar": "مجمع سكني — جدة", "en": "Residential Compound - Jeddah"},
    "Desalination Feed Line - Jubail": {"ar": "خط تغذية محطة تحلية — الجبيل", "en": "Desalination Feed Line - Jubail"},
}


def zone_label(zone_name: str, lang: str) -> str:
    """Bilingual display name for a data zone; falls back to the raw value."""
    return ZONE_NAMES.get(zone_name, {}).get(lang, zone_name)


# --------------------------------------------------------------------------
# Translations for real_dashboard.py  (published-data regional gap)
# --------------------------------------------------------------------------
REAL = {
    "ar": {
        "page_title": "فجوة استهلاك المياه — بيانات حقيقية",
        "title": "فجوة استهلاك المياه بين المناطق السعودية وهدف رؤية 2030",
        "caption": "كل رقم في هذه اللوحة مصدره منشور رسميًا — لا توجد بيانات مصطنعة هنا. انظر قسم المصادر أسفل الصفحة.",
        "kpi_excess": "الحجم الزائد وطنيًا عن هدف 2030",
        "kpi_excess_unit": "م³/سنة",
        "kpi_value": "القيمة التوضيحية (أدنى–أعلى تعرفة)",
        "kpi_value_unit": "ريال",
        "kpi_national": "فاقد الشبكة الوطني المُعلن رسميًا",
        "kpi_national_unit": "م³/يوم",
        "warning": (
            "تنويه منهجي: «القيمة التوضيحية» = الحجم الزائد أو المفقود × تعرفة رسمية حقيقية — "
            "وليست رقم إيرادات ضائعة فعليًا موثّق من شركة معينة، لأن الفاقد بطبيعته غير مفوتَر."
        ),
        "sec_lpcd": "١. استهلاك الفرد اليومي حسب المنطقة مقابل هدف 2030",
        "legend_confirmed": "رقم مؤكَّد؟",
        "confirmed_true": "مؤكَّد",
        "confirmed_false": "متوسط وطني",
        "axis_region": "المنطقة",
        "axis_lpcd": "لتر/فرد/يوم",
        "target_line": "هدف 2030: 150 لتر/فرد/يوم",
        "sec_table": "٢. جدول الفجوة الاقتصادية لكل منطقة",
        "sec_sensitivity": "٣. حساسية القيمة الاقتصادية لفاقد الشبكة الوطني حسب شريحة التعرفة",
        "radio_label": "اختر السيناريو:",
        "scenario_low": "الحد الأدنى المنشور (600 ألف م³/يوم)",
        "scenario_high": "الحد الأعلى المنشور (800 ألف م³/يوم)",
        "axis_tier": "شريحة التعرفة",
        "axis_annual_value": "القيمة السنوية التوضيحية (ريال)",
        "sec_sources": "المصادر",
        "col_region": "المنطقة",
        "col_population": "عدد السكان 2022",
        "col_lpcd": "لتر/فرد/يوم (2022)",
        "col_confirmed": "رقم مؤكَّد؟",
        "col_note": "ملاحظة",
        "col_excess_lpcd": "الزيادة عن هدف 2030 (لتر)",
        "col_excess_m3": "الفاقد السنوي (م³)",
        "col_value_low": "القيمة عند أدنى تعرفة (ريال)",
        "col_value_high": "القيمة عند أعلى تعرفة (ريال)",
    },
    "en": {
        "page_title": "Water Consumption Gap — Real Data",
        "title": "The water-consumption gap between Saudi regions and the Vision 2030 target",
        "caption": "Every figure on this dashboard comes from an officially published source — there is no synthetic data here. See the Sources section at the bottom.",
        "kpi_excess": "National volume above the 2030 target",
        "kpi_excess_unit": "m³/year",
        "kpi_value": "Illustrative value (lowest–highest tariff)",
        "kpi_value_unit": "SAR",
        "kpi_national": "Officially declared national network loss",
        "kpi_national_unit": "m³/day",
        "warning": (
            "Methodological note: the “illustrative value” = excess or lost volume × a real official tariff — "
            "it is not an actual lost-revenue figure documented by any specific utility, because network loss is by "
            "nature un-billed."
        ),
        "sec_lpcd": "1. Daily per-capita consumption by region vs. the 2030 target",
        "legend_confirmed": "Confirmed figure?",
        "confirmed_true": "Confirmed",
        "confirmed_false": "National average",
        "axis_region": "Region",
        "axis_lpcd": "Liters/person/day",
        "target_line": "2030 target: 150 L/person/day",
        "sec_table": "2. Economic-gap table by region",
        "sec_sensitivity": "3. Sensitivity of the economic value of national network loss by tariff tier",
        "radio_label": "Choose a scenario:",
        "scenario_low": "Published lower bound (600k m³/day)",
        "scenario_high": "Published upper bound (800k m³/day)",
        "axis_tier": "Tariff tier",
        "axis_annual_value": "Illustrative annual value (SAR)",
        "sec_sources": "Sources",
        "col_region": "Region",
        "col_population": "Population 2022",
        "col_lpcd": "L/person/day (2022)",
        "col_confirmed": "Confirmed?",
        "col_note": "Note",
        "col_excess_lpcd": "Excess vs. 2030 target (L)",
        "col_excess_m3": "Annual loss (m³)",
        "col_value_low": "Value at lowest tariff (SAR)",
        "col_value_high": "Value at highest tariff (SAR)",
    },
}

# Region names are stored in the data in Arabic; map them to English display.
REGION_NAMES = {
    "الرياض": "Riyadh",
    "مكة المكرمة": "Makkah",
    "المنطقة الشرقية": "Eastern Province",
    "المدينة المنورة": "Madinah",
    "عسير": "Asir",
    "جازان": "Jazan",
    "القصيم": "Qassim",
    "تبوك": "Tabuk",
    "حائل": "Hail",
    "الجوف": "Al-Jawf",
    "نجران": "Najran",
    "الحدود الشمالية": "Northern Borders",
    "الباحة": "Al-Bahah",
}

# The finite set of Arabic "note" strings produced by real_data.py, with
# English equivalents so the table's note column is bilingual too.
REGION_NOTES = {
    "رقم منشور بالتحديد لعام 2022": "Figure published specifically for 2022",
    "رقم منشور بالتحديد لعام 2022 (الأدنى وطنيًا)": "Figure published specifically for 2022 (lowest nationally)",
    "الورقة العلمية تذكر 'أقل من 120 لتر' دون رقم دقيق منشور — استخدمنا 118 كتقدير متحفظ ضمن هذا النطاق المذكور":
        "The paper states 'below 120 L' without an exact published figure — 118 is used as a conservative estimate within that stated range",
    "لا يوجد رقم إقليمي منشور — تم استخدام المتوسط الوطني الحقيقي لعام 2022 بدلاً من اختراع رقم":
        "No region-specific figure is published — the real 2022 national average is used instead of inventing a number",
}

# Tariff-tier labels (Arabic in the data) mapped to English.
TARIFF_TIERS_EN = {
    "0–15 م³/شهر": "0–15 m³/month",
    "16–30 م³/شهر": "16–30 m³/month",
    "31–45 م³/شهر": "31–45 m³/month",
    "46–60 م³/شهر": "46–60 m³/month",
    "أكثر من 60 م³/شهر": "Over 60 m³/month",
}


def region_label(region_ar: str, lang: str) -> str:
    return region_ar if lang == "ar" else REGION_NAMES.get(region_ar, region_ar)


def note_label(note_ar: str, lang: str) -> str:
    return note_ar if lang == "ar" else REGION_NOTES.get(note_ar, note_ar)


def tier_label(tier_ar: str, lang: str) -> str:
    return tier_ar if lang == "ar" else TARIFF_TIERS_EN.get(tier_ar, tier_ar)
