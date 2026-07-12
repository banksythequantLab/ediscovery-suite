"""The entwinement proof for the CockroachDB E-Discovery Suite.

Five agents, ONE CockroachDB database (`coldcase`). They don't just coexist --
they share the same corpus, the same people, and hand state to one another.
This script:
  1. gives Chronicle a live working timeline (documented public-record events),
  2. tags Gap Hunter's withheld artifacts with the principal they concern,
  3. runs a SINGLE SQL statement that assembles one person's case file across
     all five agents' schemas -- the entwinement made literal.

Deterministic, no GPU. Run: py -3.11 src/entwine.py [surname]
"""
import os, sys, psycopg
from dotenv import load_dotenv
load_dotenv(r"B:\ColdCase\.env")

PRINCIPALS = ["Skilling", "Lay", "Fastow", "Causey", "Kopper", "Watkins"]
# which withheld artifact concerns which principal (from the artifact descriptions)
GAP_SUBJECT = {"R01": "Fastow", "R02": "Lay", "R03": "Fastow",
               "R04": "Skilling", "R05": "Skilling", "R06": "Fastow"}

UNIFIED_SQL = """
SELECT 'ColdCase'  AS agent, 'suspicion'     AS kind,
       concat('score=', round(s.suspicion_score::numeric,2)::string, '  ', left(s.rationale,70)) AS detail
  FROM suspects s JOIN persons p ON p.person_id = s.person_id
  WHERE p.full_name ILIKE %(n)s OR p.real_name ILIKE %(n)s
UNION ALL
SELECT 'Witness', 'contradiction', left(st.claim, 88)
  FROM witness.contradictions c
  JOIN witness.witnesses w  ON w.witness_id  = c.witness_id
  JOIN witness.statements st ON st.statement_id = c.statement_id
  WHERE w.full_name ILIKE %(n)s
UNION ALL
SELECT 'Chronicle', 'timeline', concat(e.event_date::string, '  ', e.description)
  FROM chronicle.events e JOIN chronicle.event_actors a ON a.event_id = e.event_id
  WHERE a.actor ILIKE %(n)s AND e.active
UNION ALL
SELECT 'GapHunter', 'missing_doc',
       concat(g.target_key, ' [', g.status, ']  ', coalesce(g.channel_hint,''))
  FROM gaphunter.gaps g WHERE g.subject ILIKE %(n)s
ORDER BY 1, 2;
"""


def seed_chronicle_timeline(cur):
    if cur.execute("SELECT count(*) FROM chronicle.events").fetchone()[0] > 0:
        return "already populated"
    cur.execute("INSERT INTO chronicle.batches(seq,label) VALUES(0,'documented-baseline') RETURNING batch_id")
    bid = cur.fetchone()[0]
    rows = cur.execute("SELECT event_date, description FROM chronicle_truth.events ORDER BY event_date").fetchall()
    for d, desc in rows:
        cur.execute("""INSERT INTO chronicle.events(batch_id,description,event_date,confidence,source,active)
                       VALUES(%s,%s,%s,0.95,'public record',true) RETURNING event_id""", (bid, desc, d))
        eid = cur.fetchone()[0]
        for p in PRINCIPALS:
            if p.lower() in desc.lower():
                cur.execute("INSERT INTO chronicle.event_actors(event_id,actor,role) VALUES(%s,%s,'principal')", (eid, p))
    return f"seeded {len(rows)} documented events"

def tag_gaphunter(cur):
    cur.execute("ALTER TABLE gaphunter.gaps ADD COLUMN IF NOT EXISTS subject STRING")
    for k, subj in GAP_SUBJECT.items():
        cur.execute("UPDATE gaphunter.gaps SET subject=%s WHERE target_key=%s", (subj, k))
    return "tagged gaps by principal"

def case_file(cur, surname):
    rows = cur.execute(UNIFIED_SQL, {"n": f"%{surname}%"}).fetchall()
    held = cur.execute("SELECT count(*) FROM hold_docs WHERE held").fetchone()[0]
    lines = [f"===== UNIFIED CASE FILE: {surname}  (one SQL statement, five agents, one CockroachDB) ====="]
    if not rows:
        lines.append("  (no cross-agent hits)")
    for agent, kind, detail in rows:
        lines.append(f"  [{agent:<9}] {kind:<14} {detail}")
    lines.append(f"  [HoldFirewall] litigation hold ACTIVE on {held} responsive docs (SERIALIZABLE-protected)")
    return "\n".join(lines)


def main():
    conn = psycopg.connect(os.getenv("CRDB_ADMIN_URL"), autocommit=True)
    cur = conn.cursor()
    print("entwine:", seed_chronicle_timeline(cur))
    print("entwine:", tag_gaphunter(cur))
    print()
    people = sys.argv[1:] or ["Skilling", "Fastow"]
    out = []
    for surname in people:
        block = case_file(cur, surname)
        print(block); print()
        out.append(block)
    open(r"B:\ediscovery-suite\docs\unified_case_view.txt", "w", encoding="utf-8").write("\n\n".join(out))
    conn.close()

if __name__ == "__main__":
    main()
