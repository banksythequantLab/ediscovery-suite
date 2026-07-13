"""Entity resolution for the entwinement.

The unified case file must join agents on a RESOLVED identity, not a raw name.
The Enron corpus fragments each principal across many records (Andrew Fastow has
7: FASTOW ANDREW S, andy.fastow@, andrew.s.fastow@, andrew.fastow@ljm..., ...)
AND contains a decoy -- Lea Fastow (lfastow@) -- who must NOT resolve to Andrew.

This builds identity.entities + identity.aliases: a canonical entity per
principal, its name variants, and the specific person_ids that belong to it
(carefully excluding the wrong-person records). Deterministic custodian
resolution -- the standard e-discovery approach.
"""
import os, psycopg
from dotenv import load_dotenv
load_dotenv(r"B:\ColdCase\.env")

# canonical -> (name variants, precise person-match ILIKE patterns)
PRINCIPALS = {
 "Andrew Fastow": (
   ["Fastow","Andrew Fastow","Andy Fastow","Andrew S. Fastow","A.S. Fastow"],
   ["%FASTOW ANDREW%","andy.fastow%","andrew.fastow%","andrew.s.fastow%","s..fastow%","a..fastow%"]),
 "Jeffrey Skilling": (
   ["Skilling","Jeffrey Skilling","Jeff Skilling","Jeffrey K. Skilling"],
   ["%SKILLING JEFFREY%","jeffrey%skilling%","jeff%skilling%","jskilling@enron%","skillingj@enron%","skilling@enron.com","jeffrey.k.skilling%"]),
 "Kenneth Lay": (
   ["Lay","Kenneth Lay","Ken Lay","Kenneth L. Lay"],
   ["%LAY KENNETH%","kenneth.lay%","ken.lay%","klay@%","k..lay%"]),
 "Richard Causey": (
   ["Causey","Richard Causey","Rick Causey"],
   ["%CAUSEY RICHARD%","richard.causey%","rick.causey%","rcausey@enron%"]),
 "Michael Kopper": (
   ["Kopper","Michael Kopper","Mike Kopper"],
   ["%KOPPER%","michael.kopper%","mike.kopper%","m..kopper%"]),
 "Sherron Watkins": (
   ["Watkins","Sherron Watkins"],
   ["%WATKINS SHERRON%","sherron.watkins%","swatkins@enron%"]),
}

def main():
    c = psycopg.connect(os.getenv("CRDB_ADMIN_URL"), autocommit=True)
    c.execute("DELETE FROM identity.aliases")
    c.execute("DELETE FROM identity.entities")
    for canonical, (variants, patterns) in PRINCIPALS.items():
        eid = c.execute("INSERT INTO identity.entities(canonical) VALUES(%s) RETURNING entity_id",
                        (canonical,)).fetchone()[0]
        # name variants (no person_id)
        for v in variants:
            c.execute("INSERT INTO identity.aliases(entity_id,alias,person_id) VALUES(%s,%s,NULL) "
                      "ON CONFLICT DO NOTHING", (eid, v))
        # resolve to specific person records via precise patterns
        person_ids = set(); matched = []
        for p in patterns:
            for pid, nm in c.execute(
                "SELECT person_id, coalesce(real_name,full_name) FROM persons "
                "WHERE full_name ILIKE %s OR coalesce(real_name,'') ILIKE %s", (p, p)).fetchall():
                if pid not in person_ids:
                    person_ids.add(pid); matched.append(nm)
                    c.execute("INSERT INTO identity.aliases(entity_id,alias,person_id) VALUES(%s,%s,%s) "
                              "ON CONFLICT DO NOTHING", (eid, nm, pid))
        print(f"{canonical:<18} -> {len(person_ids)} person records: {matched}")
    # sanity: Lea Fastow must NOT be resolved to Andrew
    lea = c.execute("SELECT count(*) FROM identity.aliases a JOIN persons p ON p.person_id=a.person_id "
                    "WHERE p.full_name ILIKE '%lfastow%'").fetchone()[0]
    print(f"\nDECOY CHECK -- Lea Fastow (lfastow) records wrongly resolved: {lea}  (must be 0)")
    c.close()

if __name__ == "__main__":
    main()
