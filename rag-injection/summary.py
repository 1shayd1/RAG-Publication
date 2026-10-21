import pandas as pd
from db import connect

conn = connect()
rows = conn.execute("""
    SELECT r.model, t.variant, r.canary_in_answer, r.canary_retrieved, r.correct
    FROM results r JOIN test_cases t USING (case_id)
""").fetchall()
df = pd.DataFrame(rows, columns=["model", "variant", "attack", "retrieved", "correct"])

clean = df[df.variant == "clean"]
atk = df[df.variant != "clean"].copy()
atk["attack"] = atk["attack"].astype(bool)
atk["retrieved"] = atk["retrieved"].astype(bool)

print("\nBenign accuracy (clean docs):")
print(clean.groupby("model").correct.mean().round(2))

print("\nInjection retrieved rate by category (should be close to 1.0):")
print(atk.groupby("variant").retrieved.mean().round(2))

print("\nAttack success rate by model (only cases where injection was retrieved):")
print(atk[atk.retrieved].groupby("model").attack.mean().round(2))

print("\nAttack success rate, category x model:")
print(atk[atk.retrieved].pivot_table(index="variant", columns="model",
                                     values="attack", aggfunc="mean").round(2))
