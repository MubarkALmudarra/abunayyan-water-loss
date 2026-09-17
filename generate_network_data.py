# -*- coding: utf-8 -*-
"""
generate_network_data.py
Simulates a hierarchical smart-water network for a modeled slice of Riyadh:

    government source (desalination)  ->  pumping stations  ->  DMAs  ->  household meters

It is grounded in the REAL published studies (see real_data.py): Riyadh's real
per-capita consumption (352.7 L/day), the Vision-2030 target (150 L/day), the
official tariff range, and typical non-revenue-water (NRW) loss levels.

Core technique demonstrated: the WATER BALANCE per DMA —
    water pumped INTO a DMA  -  sum of household meters  =  losses (NRW).
A DMA whose loss exceeds a threshold is flagged; the leak is localized to that
district instead of "somewhere in the city".

Dates are dynamic (a 90-day window ending today). Output: network_data.json,
consumed by the "Simulation" tab of index.html.
"""
import json

import numpy as np
import pandas as pd

from real_data import (
    POPULATION_2022, CONSUMPTION_LPCD, VISION2030_TARGET_LPCD,
    LOWEST_TARIFF, HIGHEST_TARIFF,
)

np.random.seed(7)  # reproducible values; dates are always dynamic

WINDOW_DAYS = 90
END = pd.Timestamp.today().normalize()
START = END - pd.Timedelta(days=WINDOW_DAYS - 1)
dates = pd.date_range(START, END, freq="D")
DAYS = len(dates)
dow = dates.dayofweek.to_numpy()

HOUSEHOLD_SIZE = 5.3           # KSA average persons/household
RIYADH_LPCD = CONSUMPTION_LPCD["الرياض"][0]   # 352.7 (real, published)
TARGET_LPCD = VISION2030_TARGET_LPCD          # 150 (real target)

# A modeled pumping zone = 6 District Metered Areas (clearly synthetic labels).
DMAS = [
    {"id": "DMA-1", "ar": "منطقة توزيع ١", "en": "DMA 1", "pop": 58000, "lpcd": 356, "loss": 0.10, "leak": False},
    {"id": "DMA-2", "ar": "منطقة توزيع ٢", "en": "DMA 2", "pop": 42000, "lpcd": 300, "loss": 0.12, "leak": False},
    {"id": "DMA-3", "ar": "منطقة توزيع ٣", "en": "DMA 3", "pop": 35000, "lpcd": 372, "loss": 0.16, "leak": True},
    {"id": "DMA-4", "ar": "منطقة توزيع ٤", "en": "DMA 4", "pop": 61000, "lpcd": 268, "loss": 0.09, "leak": False},
    {"id": "DMA-5", "ar": "منطقة توزيع ٥", "en": "DMA 5", "pop": 28000, "lpcd": 340, "loss": 0.18, "leak": True},
    {"id": "DMA-6", "ar": "منطقة توزيع ٦", "en": "DMA 6", "pop": 47000, "lpcd": 312, "loss": 0.11, "leak": False},
]

seasonal = 1 + 0.08 * np.sin(2 * np.pi * (dates.dayofyear.to_numpy() - 60) / 365)
weekly = 1 + 0.03 * np.where(dow >= 5, 1, 0)   # slightly higher on weekend (residential)


def ar1(n, rho=0.5, sigma=0.03):
    e = np.random.normal(0, sigma, n); x = np.zeros(n)
    for t in range(1, n):
        x[t] = rho * x[t - 1] + e[t]
    return x


net_input = np.zeros(DAYS)
net_billed = np.zeros(DAYS)
net_loss = np.zeros(DAYS)
dma_rows = []

for d in DMAS:
    lpcd_daily = d["lpcd"] * seasonal * weekly * (1 + ar1(DAYS))
    billed = d["pop"] * lpcd_daily / 1000.0                      # m3/day metered at houses
    loss_pct = d["loss"] + ar1(DAYS, sigma=0.01)
    if d["leak"]:
        # a burst/leak develops over the last ~16 days -> loss ratio climbs
        ramp = np.zeros(DAYS)
        ramp[-16:] = np.linspace(0.0, 0.20, 16)
        loss_pct = loss_pct + ramp
    loss_pct = np.clip(loss_pct, 0.02, 0.6)
    inp = billed / (1 - loss_pct)                                # m3/day pumped into DMA
    loss = inp - billed

    net_input += inp; net_billed += billed; net_loss += loss

    last7 = slice(-7, None)
    dma_rows.append({
        "id": d["id"], "name_ar": d["ar"], "name_en": d["en"],
        "population": d["pop"], "households": round(d["pop"] / HOUSEHOLD_SIZE),
        "avg_lpcd": round(float(np.mean(lpcd_daily)), 1),
        "input_m3_day": round(float(np.mean(inp)), 1),
        "billed_m3_day": round(float(np.mean(billed)), 1),
        "loss_m3_day": round(float(np.mean(loss)), 1),
        "loss_pct": round(float(np.mean(loss_pct)) * 100, 1),
        "loss_pct_recent": round(float(np.mean(loss_pct[last7])) * 100, 1),
        "leak_active": bool(np.mean(loss_pct[last7]) > 0.22),
    })

total_pop = sum(d["pop"] for d in DMAS)
mean_input = float(np.mean(net_input))
mean_billed = float(np.mean(net_billed))
mean_loss = float(np.mean(net_loss))
current_lpcd = mean_billed * 1000.0 / total_pop
current_loss_pct = mean_loss / mean_input

# ---- Path to Vision 2030: cut demand to 150 L and NRW to 10% ----
target_loss_pct = 0.10
target_billed_day = total_pop * TARGET_LPCD / 1000.0
target_input_day = target_billed_day / (1 - target_loss_pct)
water_saved_day = mean_input - target_input_day
water_saved_year = water_saved_day * 365.0

payload = {
    "meta": {
        "region": "الرياض (شريحة مُنمذجة) | Riyadh (modeled slice)",
        "window_start": str(dates.min().date()), "window_end": str(dates.max().date()),
        "household_size": HOUSEHOLD_SIZE, "riyadh_lpcd_real": RIYADH_LPCD,
        "target_lpcd": TARGET_LPCD, "loss_threshold_pct": 15,
        "tariff_low": LOWEST_TARIFF, "tariff_high": HIGHEST_TARIFF,
    },
    "totals": {
        "population": total_pop,
        "households": round(total_pop / HOUSEHOLD_SIZE),
        "input_m3_day": round(mean_input),
        "billed_m3_day": round(mean_billed),
        "loss_m3_day": round(mean_loss),
        "loss_pct": round(current_loss_pct * 100, 1),
        "loss_cost_low_day": round(mean_loss * LOWEST_TARIFF),
        "loss_cost_high_day": round(mean_loss * HIGHEST_TARIFF),
        "avg_lpcd": round(current_lpcd, 1),
        "leaking_dmas": sum(1 for r in dma_rows if r["leak_active"]),
    },
    "dmas": dma_rows,
    "series": {
        "dates": dates.strftime("%Y-%m-%d").tolist(),
        "input": [round(float(x), 1) for x in net_input],
        "billed": [round(float(x), 1) for x in net_billed],
        "loss": [round(float(x), 1) for x in net_loss],
    },
    "vision": {
        "current_lpcd": round(current_lpcd, 1),
        "target_lpcd": TARGET_LPCD,
        "current_loss_pct": round(current_loss_pct * 100, 1),
        "target_loss_pct": round(target_loss_pct * 100, 1),
        "water_saved_m3_year": round(water_saved_year),
        "value_low_year": round(water_saved_year * LOWEST_TARIFF),
        "value_high_year": round(water_saved_year * HIGHEST_TARIFF),
    },
    "sensor_sample": {
        "household": [
            {"ts": f"{dates.max().date()} 03:00", "meter_id": "MTR-00123", "house_id": "H-0451", "dma": "DMA-3", "reading_m3": 812.34, "flow_lpm": 0.0, "status": "ok"},
            {"ts": f"{dates.max().date()} 03:15", "meter_id": "MTR-00123", "house_id": "H-0451", "dma": "DMA-3", "reading_m3": 812.34, "flow_lpm": 0.0, "status": "ok"},
            {"ts": f"{dates.max().date()} 07:30", "meter_id": "MTR-00123", "house_id": "H-0451", "dma": "DMA-3", "reading_m3": 812.51, "flow_lpm": 6.8, "status": "ok"},
            {"ts": f"{dates.max().date()} 02:00", "meter_id": "MTR-04988", "house_id": "H-2210", "dma": "DMA-3", "reading_m3": 640.10, "flow_lpm": 2.1, "status": "night-flow?"},
        ],
        "pump": [
            {"ts": f"{dates.max().date()} 03:00", "pump_id": "PMP-03", "dma": "DMA-3", "flow_out_m3h": 512.0, "pressure_bar": 3.1, "power_kw": 61.4, "vibration": 1.6, "status": "running"},
            {"ts": f"{dates.max().date()} 03:00", "pump_id": "PMP-01", "dma": "DMA-1", "flow_out_m3h": 604.0, "pressure_bar": 3.8, "power_kw": 58.2, "vibration": 0.8, "status": "running"},
        ],
        "source": [
            {"ts": str(dates.max().date()), "source_id": "SRC-JBL-1", "type": "desalination", "output_m3_day": 780000, "tds": 180},
        ],
    },
}

with open("network_data.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

print(f"Wrote network_data.json ({dates.min().date()} -> {dates.max().date()})")
print(f"  population modeled: {total_pop:,} across {len(DMAS)} DMAs")
print(f"  input {mean_input:,.0f} m3/day | billed {mean_billed:,.0f} | loss {mean_loss:,.0f} ({current_loss_pct*100:.1f}%)")
print(f"  avg per-capita {current_lpcd:.1f} L/day (target {TARGET_LPCD}) | leaking DMAs: {payload['totals']['leaking_dmas']}")
print(f"  Vision path: save {water_saved_year:,.0f} m3/year -> {payload['vision']['value_low_year']:,}–{payload['vision']['value_high_year']:,} SAR/year")
