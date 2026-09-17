"""
بيانات حقيقية موثّقة المصدر — لا بيانات مصطنعة هنا.
كل رقم في هذا الملف له مصدر منشور فعليًا (رابط + سنة).
"""

SOURCES = {
    "mdpi_consumption": {
        "title": "Regional Heterogeneity in Urban Water Consumption in Saudi Arabia (MDPI Water, 2025)",
        "url": "https://www.mdpi.com/2073-4441/17/8/1156",
    },
    "census_2022": {
        "title": "تعداد السعودية 2022 - الهيئة العامة للإحصاء (عبر ويكيبيديا)",
        "url": "https://ar.wikipedia.org/wiki/%D8%AA%D8%B9%D8%AF%D8%A7%D8%AF_%D8%A7%D9%84%D8%B3%D8%B9%D9%88%D8%AF%D9%8A%D8%A9_2022",
    },
    "tariff": {
        "title": "التعرفة الجديدة للمياه وتوزيعها على الشرائح - أرقام",
        "url": "https://www.argaam.com/ar/article/articledetail/id/416258",
    },
    "nrw_loss": {
        "title": "Saudi Arabia's Water Sector - US-Saudi Business Council Economic Brief (Feb 2022)",
        "url": "https://ussaudi.org/wp-content/uploads/2022/02/Water-2022-Economic-Brief.pdf",
    },
    "vision2030_target": {
        "title": "National Water Strategy target (263L -> 150L by 2030), cited in US-Saudi Business Council brief",
        "url": "https://ussaudi.org/wp-content/uploads/2022/02/Water-2022-Economic-Brief.pdf",
    },
}

# ---- Real 2022 census population by administrative region ----
# Source: census_2022
POPULATION_2022 = {
    "الرياض":            8_591_748,
    "مكة المكرمة":        8_021_463,
    "المنطقة الشرقية":    5_125_254,
    "المدينة المنورة":    2_137_983,
    "عسير":              2_024_285,
    "جازان":             1_404_997,
    "القصيم":            1_336_179,
    "تبوك":                886_036,
    "حائل":                746_406,
    "الجوف":               595_822,
    "نجران":               592_300,
    "الحدود الشمالية":     373_577,
    "الباحة":              339_174,
}
TOTAL_POPULATION_2022 = 32_175_224

# ---- Real per-capita daily consumption (liters/person/day), 2022 ----
# CONFIRMED = published exact figure in the peer-reviewed source (mdpi_consumption)
# NATIONAL_AVG = no region-specific published figure found; national average used explicitly (not invented)
NATIONAL_AVG_LPCD_2022 = 299.0   # confirmed national figure, mdpi_consumption
NATIONAL_AVG_LPCD_2010 = 272.0   # confirmed national figure, mdpi_consumption
VISION2030_TARGET_LPCD = 150.0   # confirmed target, vision2030_target (from 263 -> 150 by 2030)

CONSUMPTION_LPCD = {
    # region: (value, is_confirmed, note)
    "الرياض":         (352.7, True,  "رقم منشور بالتحديد لعام 2022"),
    "المنطقة الشرقية": (368.0, True,  "رقم منشور بالتحديد لعام 2022"),
    "نجران":          (143.2, True,  "رقم منشور بالتحديد لعام 2022 (الأدنى وطنيًا)"),
    "عسير":           (118.0, False, "الورقة العلمية تذكر 'أقل من 120 لتر' دون رقم دقيق منشور — استخدمنا 118 كتقدير متحفظ ضمن هذا النطاق المذكور"),
    "جازان":          (118.0, False, "الورقة العلمية تذكر 'أقل من 120 لتر' دون رقم دقيق منشور — استخدمنا 118 كتقدير متحفظ ضمن هذا النطاق المذكور"),
    # الباقي: لا يوجد رقم إقليمي منشور بالتحديد -> نستخدم المتوسط الوطني الحقيقي صراحة (وليس رقمًا مختلقًا)
    "مكة المكرمة":     (NATIONAL_AVG_LPCD_2022, False, "لا يوجد رقم إقليمي منشور — تم استخدام المتوسط الوطني الحقيقي لعام 2022 بدلاً من اختراع رقم"),
    "المدينة المنورة": (NATIONAL_AVG_LPCD_2022, False, "لا يوجد رقم إقليمي منشور — تم استخدام المتوسط الوطني الحقيقي لعام 2022 بدلاً من اختراع رقم"),
    "القصيم":         (NATIONAL_AVG_LPCD_2022, False, "لا يوجد رقم إقليمي منشور — تم استخدام المتوسط الوطني الحقيقي لعام 2022 بدلاً من اختراع رقم"),
    "تبوك":           (NATIONAL_AVG_LPCD_2022, False, "لا يوجد رقم إقليمي منشور — تم استخدام المتوسط الوطني الحقيقي لعام 2022 بدلاً من اختراع رقم"),
    "حائل":           (NATIONAL_AVG_LPCD_2022, False, "لا يوجد رقم إقليمي منشور — تم استخدام المتوسط الوطني الحقيقي لعام 2022 بدلاً من اختراع رقم"),
    "الجوف":          (NATIONAL_AVG_LPCD_2022, False, "لا يوجد رقم إقليمي منشور — تم استخدام المتوسط الوطني الحقيقي لعام 2022 بدلاً من اختراع رقم"),
    "الحدود الشمالية": (NATIONAL_AVG_LPCD_2022, False, "لا يوجد رقم إقليمي منشور — تم استخدام المتوسط الوطني الحقيقي لعام 2022 بدلاً من اختراع رقم"),
    "الباحة":         (NATIONAL_AVG_LPCD_2022, False, "لا يوجد رقم إقليمي منشور — تم استخدام المتوسط الوطني الحقيقي لعام 2022 بدلاً من اختراع رقم"),
}

# ---- Real official domestic tariff tiers (SAR per m3, water+sewage combined) ----
# Source: tariff
TARIFF_TIERS = [
    {"tier": "0–15 م³/شهر",  "rate_sar_per_m3": 0.15},
    {"tier": "16–30 م³/شهر", "rate_sar_per_m3": 1.50},
    {"tier": "31–45 م³/شهر", "rate_sar_per_m3": 4.50},
    {"tier": "46–60 م³/شهر", "rate_sar_per_m3": 6.00},
    {"tier": "أكثر من 60 م³/شهر", "rate_sar_per_m3": 9.00},
]
LOWEST_TARIFF = 0.15
HIGHEST_TARIFF = 9.00

# ---- Real published national network loss (before reaching end users) ----
# Source: nrw_loss  ("600-800 thousand m3/day loss before reaching end users")
NATIONAL_DAILY_LOSS_M3_LOW = 600_000
NATIONAL_DAILY_LOSS_M3_HIGH = 800_000
