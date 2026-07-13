"""CockroachDB row-level security as a legal ETHICAL WALL + privilege screen.

The legal industry's #1 concern about shared AI memory is cross-matter
contamination and privilege waiver. Here the database itself enforces it: a
reviewer physically cannot SELECT another matter's rows, and no ordinary
reviewer can read privileged rows -- only the privilege team can. Enforced by
RLS policies scoped to roles, not by application code.

Run: py -3.11 src/prove_ethwall.py   (writes docs/ethwall_proof.txt)
"""
import os, psycopg
from dotenv import load_dotenv
load_dotenv(r"B:\ColdCase\.env")

DDL = [
 "DROP TABLE IF EXISTS rls_probe",
 "CREATE SCHEMA IF NOT EXISTS ethwall",
 "DROP TABLE IF EXISTS ethwall.documents CASCADE",
 "CREATE TABLE ethwall.documents(doc_id INT PRIMARY KEY, matter STRING, is_privileged BOOL, title STRING)",
 "INSERT INTO ethwall.documents VALUES "
 "(1,'A',false,'Matter A - responsive email'),"
 "(2,'A',true ,'Matter A - PRIVILEGED counsel memo'),"
 "(3,'B',false,'Matter B - responsive email'),"
 "(4,'B',true ,'Matter B - PRIVILEGED strategy note')",
 "ALTER TABLE ethwall.documents ENABLE ROW LEVEL SECURITY",
 "ALTER TABLE ethwall.documents FORCE ROW LEVEL SECURITY",
 "CREATE ROLE IF NOT EXISTS reviewer_a",
 "CREATE ROLE IF NOT EXISTS reviewer_b",
 "CREATE ROLE IF NOT EXISTS privilege_team",
 "GRANT USAGE ON SCHEMA ethwall TO reviewer_a, reviewer_b, privilege_team",
 "GRANT SELECT ON ethwall.documents TO reviewer_a, reviewer_b, privilege_team",
 "DROP POLICY IF EXISTS wall_a ON ethwall.documents",
 "DROP POLICY IF EXISTS wall_b ON ethwall.documents",
 "DROP POLICY IF EXISTS priv_all ON ethwall.documents",
 "CREATE POLICY wall_a ON ethwall.documents TO reviewer_a USING (matter='A' AND NOT is_privileged)",
 "CREATE POLICY wall_b ON ethwall.documents TO reviewer_b USING (matter='B' AND NOT is_privileged)",
 "CREATE POLICY priv_all ON ethwall.documents TO privilege_team USING (true)",
]

def see(cur, role):
    cur.execute(f"SET ROLE {role}")
    rows = cur.execute("SELECT matter, is_privileged, title FROM ethwall.documents ORDER BY doc_id").fetchall()
    cur.execute("RESET ROLE")
    return rows

def main():
    import io, contextlib
    c = psycopg.connect(os.getenv("CRDB_ADMIN_URL"), autocommit=True); cur = c.cursor()
    for stmt in DDL:
        cur.execute(stmt)
    out = []
    out.append("CockroachDB Row-Level Security ethical wall + privilege screen")
    out.append("4 documents: Matter A (1 responsive, 1 privileged), Matter B (same).\n")
    for role, note in [("reviewer_a","assigned to Matter A"),
                       ("reviewer_b","assigned to Matter B"),
                       ("privilege_team","the privilege review team")]:
        rows = see(cur, role)
        out.append(f"[{role}] ({note}) can SELECT {len(rows)} row(s):")
        for m, pr, t in rows:
            out.append(f"    matter {m} {'PRIVILEGED' if pr else 'responsive '}  {t}")
        out.append("")
    a = see(cur, "reviewer_a"); b = see(cur, "reviewer_b")
    a_sees_b = any(m == "B" for m, _, _ in a)
    a_sees_priv = any(pr for _, pr, _ in a)
    out.append(f"WALL CHECK -- reviewer_a can see any Matter B row: {a_sees_b}  (must be False)")
    out.append(f"PRIVILEGE  -- reviewer_a can see any privileged row: {a_sees_priv}  (must be False)")
    out.append("The database -- not the app -- physically enforces the wall. A cross-matter")
    out.append("or privileged read returns zero rows, not a filtered-in-code result.")
    text = "\n".join(out)
    print(text)
    open(r"B:\ediscovery-suite\docs\ethwall_proof.txt", "w", encoding="utf-8").write(text)
    c.close()

if __name__ == "__main__":
    main()
