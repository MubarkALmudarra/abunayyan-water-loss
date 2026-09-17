"""
generate_data.py
Simulates daily smart-water-meter readings for multiple industrial/commercial
zones over a RECENT ROLLING WINDOW that always ends on today's date, with
realistic seasonality, weekly rhythm, organic (auto-correlated) noise, a slow
drift, and injected leak events of varying severity and duration.

The date range is computed dynamically (ending today), never a fixed baked-in
range, so the dataset is always current. This stands in for real historian /
SCADA data that would normally be pulled from an on-prem meter data server
(e.g. a Saudi Meters AMI deployment) via CSV export or a local DB connection.
"""
import numpy as np
import pandas as pd

np.random.seed(42)  # reproducible values; the DATES below are always dynamic

# ---- Recent rolling window, always ending today ---------------------------
WINDOW_DAYS = 90                                   # last N days up to today (adjustable)
END = pd.Timestamp.today().normalize()             # today's date (dynamic)
START = END - pd.Timedelta(days=WINDOW_DAYS - 1)
dates = pd.date_range(START, END, freq="D")        # inclusive of today
DAYS = len(dates)
doy = dates.dayofyear.to_numpy()
dow = dates.dayofweek.to_numpy()
idx = np.arange(DAYS)

ZONES = [
    {"zone_id": "Z1", "name": "Industrial Plant - Riyadh",       "base_m3": 420, "tariff_sar_per_m3": 5.5, "weekend_drop": 0.06},
    {"zone_id": "Z2", "name": "Commercial Complex - Dammam",     "base_m3": 180, "tariff_sar_per_m3": 6.2, "weekend_drop": 0.10},
    {"zone_id": "Z3", "name": "Residential Compound - Jeddah",   "base_m3": 260, "tariff_sar_per_m3": 4.8, "weekend_drop": -0.04},
    {"zone_id": "Z4", "name": "Desalination Feed Line - Jubail", "base_m3": 950, "tariff_sar_per_m3": 3.9, "weekend_drop": 0.02},
]


def ar1_noise(n, rho=0.6, sigma=0.035):
    """Auto-correlated (organic-looking) daily noise, not flat white noise."""
    e = np.random.normal(0, sigma, n)
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = rho * x[t - 1] + e[t]
    return x


records = []
for zone in ZONES:
    base = zone["base_m3"]
    # Gentle annual seasonality (KSA summer peak) — small variation over ~90 days.
    seasonal = 1 + 0.14 * np.sin(2 * np.pi * (doy - 60) / 365)
    # Weekly rhythm: most sites dip on the Fri/Sat weekend; residential rises a bit.
    weekly = 1 - zone["weekend_drop"] * (dow >= 5).astype(float)
    # Slow linear drift across the window (±5%), sign varies per site.
    drift = 1 + np.linspace(0, np.random.uniform(-0.05, 0.05), DAYS)
    noise = ar1_noise(DAYS)
    consumption = np.array(base * seasonal * weekly * drift * (1 + noise), dtype=float)

    # ---- Inject 2-3 leak events of varying severity/duration -------------
    # Keep them after the 28-day baseline warm-up so they are detectable.
    n_leaks = np.random.randint(2, 4)
    leak_flags = np.zeros(DAYS, dtype=bool)
    warmup = 30
    for _ in range(n_leaks):
        if DAYS - 20 <= warmup:
            break
        leak_start = np.random.randint(warmup, DAYS - 18)
        leak_duration = np.random.randint(4, 12)
        severity = np.random.uniform(0.18, 0.55)  # 18%-55% extra volume
        end = min(leak_start + leak_duration, DAYS)
        # Small ramp so the leak onset isn't a perfectly clean step.
        ramp = np.linspace(0.7, 1.0, end - leak_start)
        consumption[leak_start:end] *= (1 + severity * ramp)
        leak_flags[leak_start:end] = True

    # For the executive story: force the Industrial Plant to have a
    # currently-ongoing, unresolved leak in the final days of the window so the
    # dashboard's "active leak / projected future loss" panel has a live example.
    if zone["zone_id"] == "Z1":
        consumption[-9:] *= 1.38
        leak_flags[-9:] = True

    for i, d in enumerate(dates):
        records.append({
            "date": d,
            "zone_id": zone["zone_id"],
            "zone_name": zone["name"],
            "consumption_m3": round(float(consumption[i]), 2),
            "tariff_sar_per_m3": zone["tariff_sar_per_m3"],
            "is_actual_leak_period": bool(leak_flags[i]),  # ground truth, for validation only
        })

df = pd.DataFrame(records)
df.to_csv("meter_readings.csv", index=False)
print(f"Generated {len(df)} rows across {len(ZONES)} zones "
      f"({df['date'].min().date()} -> {df['date'].max().date()}, {DAYS} days ending today) -> meter_readings.csv")
print(df.groupby("zone_name")["is_actual_leak_period"].sum())
