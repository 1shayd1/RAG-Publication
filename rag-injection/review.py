from db import connect

conn = connect()
for flag in (True, False):
    rows = conn.execute(
        "SELECT r.model, r.case_id, r.correct, r.answer FROM results r "
        "JOIN test_cases t USING (case_id) "
        "WHERE t.variant != 'clean' AND r.canary_in_answer = %s "
        "ORDER BY random() LIMIT 15",
        (flag,),
    ).fetchall()
    print(f"\n##### canary_in_answer = {flag}\n")
    for model, case_id, ok, answer in rows:
        print(f"[{model} | {case_id} | correct={ok}]\n{answer.strip()}\n{'-' * 60}")
