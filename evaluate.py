"""
evaluate.py
Since this demo uses simulated data with a known ground truth
(is_actual_leak_period), we can report real precision/recall numbers.
On a live deployment this same script would instead compare against
maintenance-log-confirmed leak incidents.
"""
from analysis import load_data, build_baseline, detect_anomalies

raw = load_data()
scored = detect_anomalies(build_baseline(raw))

tp = ((scored.predicted_leak) & (scored.is_actual_leak_period)).sum()
fp = ((scored.predicted_leak) & (~scored.is_actual_leak_period)).sum()
fn = ((~scored.predicted_leak) & (scored.is_actual_leak_period)).sum()
tn = ((~scored.predicted_leak) & (~scored.is_actual_leak_period)).sum()

precision = tp / (tp + fp) if (tp + fp) else 0
recall = tp / (tp + fn) if (tp + fn) else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

print("=== Detection Quality (vs. simulated ground truth) ===")
print(f"True Positives : {tp}")
print(f"False Positives: {fp}")
print(f"False Negatives: {fn}")
print(f"True Negatives : {tn}")
print(f"Precision      : {precision:.2%}")
print(f"Recall         : {recall:.2%}")
print(f"F1 Score       : {f1:.2%}")
