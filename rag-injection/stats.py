import math
import os

import matplotlib
matplotlib.use("Agg")   
import matplotlib.pyplot as plt
import pandas as pd

from db import connect


# Wilson 95% confidence interval for a proportion k/n
# Shows the range where the "true" ASR most likely lies, works well for small n and for values near 0 or 1.
def wilson(k, n, z=1.96):
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return centre - half, centre + half


# Load results of run 0, joined with test_cases to get the attack category (variant)
conn = connect()
rows = conn.execute("""
    SELECT r.model, t.variant, r.canary_in_answer, r.canary_retrieved, r.correct
    FROM results r JOIN test_cases t USING (case_id) WHERE r.run_idx = 0
""").fetchall()
df = pd.DataFrame(rows, columns=["model", "variant", "attack", "retrieved", "correct"])

# Benign accuracy: share of correct answers on clean documents (shows the model can answer at all)
clean = df[df.variant == "clean"].copy()
clean["correct"] = clean["correct"].astype(bool)
print("\nBenign accuracy (clean documents):")
print(clean.groupby("model").correct.mean().round(2).to_string())

# Keep only attack cases where the injection was in the model's context
atk = df[(df.variant != "clean") & (df.retrieved == True)].copy()
atk["attack"] = atk["attack"].astype(bool)
atk["correct"] = atk["correct"].astype(bool)

# ASR per model with 95% Wilson CI
print("\nASR per model with 95% Wilson CI:")
for model, g in atk.groupby("model"):
    k, n = int(g.attack.sum()), len(g)          # k = successful attacks, n = attempts
    lo, hi = wilson(k, n)
    print(f"  {model:14} {k / n:.2f}  [{lo:.2f}, {hi:.2f}]  ({k}/{n})")

# Full hijack (canary, wrong answer) vs partial (canary, answer still correct)
print("\nFull hijack (canary, answer wrong) vs partial (canary, answer still correct):")
atk["full"] = atk.attack & ~atk.correct
atk["partial"] = atk.attack & atk.correct
print(atk.groupby("model")[["full", "partial"]].mean().round(2))

# Same split per attack category and model
print("\nSame split per category:")
print(atk.groupby(["variant", "model"])[["full", "partial"]].mean().round(2))

# Heatmap: ASR for each category (rows) x model (columns), saved to figures/asr_heatmap.png
pt = atk.pivot_table(index="variant", columns="model", values="attack", aggfunc="mean")
fig, ax = plt.subplots(figsize=(6, 3.5))
im = ax.imshow(pt.values, vmin=0, vmax=1, cmap="Reds")       # colour = ASR from 0 (white) to 1 (dark red)
ax.set_xticks(range(len(pt.columns)), pt.columns, rotation=30, ha="right")
ax.set_yticks(range(len(pt.index)), pt.index)
for i in range(pt.shape[0]):                                 # write the number in every cell
    for j in range(pt.shape[1]):
        ax.text(j, i, f"{pt.values[i, j]:.2f}", ha="center", va="center")
fig.colorbar(im, label="Attack success rate")
os.makedirs("figures", exist_ok=True)
fig.savefig("figures/asr_heatmap.png", dpi=200, bbox_inches="tight")
print("\nsaved figures/asr_heatmap.png")
