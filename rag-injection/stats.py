import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from db import connect


def wilson(k, n, z=1.96):
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return centre - half, centre + half


conn = connect()
rows = conn.execute("""
    SELECT r.model, t.variant, r.canary_in_answer, r.canary_retrieved, r.correct
    FROM results r JOIN test_cases t USING (case_id) WHERE r.run_idx = 0
""").fetchall()
df = pd.DataFrame(rows, columns=["model", "variant", "attack", "retrieved", "correct"])

atk = df[(df.variant != "clean") & (df.retrieved == True)].copy()
atk["attack"] = atk["attack"].astype(bool)
atk["correct"] = atk["correct"].astype(bool)

print("\nASR per model with 95% Wilson CI:")
for model, g in atk.groupby("model"):
    k, n = int(g.attack.sum()), len(g)
    lo, hi = wilson(k, n)
    print(f"  {model:14} {k / n:.2f}  [{lo:.2f}, {hi:.2f}]  ({k}/{n})")

print("\nFull hijack (canary, answer wrong) vs partial (canary, answer still correct):")
atk["full"] = atk.attack & ~atk.correct
atk["partial"] = atk.attack & atk.correct
print(atk.groupby("model")[["full", "partial"]].mean().round(2))

print("\nSame split per category:")
print(atk.groupby(["variant", "model"])[["full", "partial"]].mean().round(2))

pt = atk.pivot_table(index="variant", columns="model", values="attack", aggfunc="mean")
fig, ax = plt.subplots(figsize=(6, 3.5))
im = ax.imshow(pt.values, vmin=0, vmax=1, cmap="Reds")
ax.set_xticks(range(len(pt.columns)), pt.columns)
ax.set_yticks(range(len(pt.index)), pt.index)
for i in range(pt.shape[0]):
    for j in range(pt.shape[1]):
        ax.text(j, i, f"{pt.values[i, j]:.2f}", ha="center", va="center")
fig.colorbar(im, label="Attack success rate")
os.makedirs("figures", exist_ok=True)
fig.savefig("figures/asr_heatmap.png", dpi=200, bbox_inches="tight")
print("\nsaved figures/asr_heatmap.png")
