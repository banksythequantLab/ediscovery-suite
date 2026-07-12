# Nota.Lawyer — a CockroachDB E-Discovery Suite

**Submission · CockroachDB × AWS "Build with Agentic Memory"**

*Five specialized legal agents. One entwined CockroachDB memory. Every one of
them proves that persistent memory doesn't just make an agent faster — it
changes the outcome.*

## Inspiration

E-discovery is the part of litigation where cases are won or lost in the
documents — and it is drowning in them. Modern "AI review" tools are stateless:
they embed a batch, answer, and forget. But the hardest e-discovery questions
are about *relationships across time* — a witness contradicts himself six weeks
apart; a document that should exist never arrives; a theory of the case shifts
as new evidence lands. Those questions are unanswerable without memory. So we
asked: what could an agent do if its memory were a real, transactional,
multi-modal database instead of a vector cache? We answered it five times, on
the most famous document set in legal history — the Enron corpus.

## What it does

One CockroachDB database (`coldcase`) backs five agents that share the same
corpus, people, and case memory:

- **Cold Case** — investigates the fraud *blind* (convictions sealed by RBAC)
  over 500K+ emails and 22 SEC filings, and independently names the real
  persons of interest with evidence trails.
- **Chronicle** — maintains a *living theory of the case*: a timeline that
  accumulates and stabilizes as evidence arrives.
- **Witness** — assembles an *impeachment file*: every collision between a
  witness's words and the documentary record.
- **Gap Hunter** — finds what's **missing**: orphaned attachments, referenced-
  but-absent minutes, off-channel "text me" gaps — a prioritized subpoena list.
- **Hold Firewall** — a real-time *spoliation guard*: under SERIALIZABLE, a
  litigation hold cannot be raced by concurrent deletion.

Because they live in one database, **a single SQL statement assembles any
person's complete case file across all five agents.** The sharpest proof:
Cold Case never flagged Andrew Fastow from email alone — yet the same query
surfaces his timeline, his testimony contradictions, and three withheld
documents from the other agents. No single tool saw him; the entwined memory did.

## Every agent proves memory changes the outcome

Each agent ships an **objective memory ablation** — the identical experiment run
with persistent memory on and off:

| Agent | Memory ON | Memory OFF |
|---|---|---|
| Cold Case | 4/18 POIs, 100% precision | 0 |
| Chronicle | theory converges to truth (0.98) | oscillates, lands wrong (0.42) |
| Witness | 12/12 contradictions retained | 3/12 (cross-batch ones lost) |
| Gap Hunter | 6/6 gaps, 100% precision | buried in 16 flags (37%) |
| Hold Firewall | 0 documents destroyed | ~119 destroyed (spoliation) |

## How we built it

- **CockroachDB Cloud (v25.4)** as the single memory substrate: `persons`,
  500K+ `emails`, C-SPANN vector indexes on email + filing chunks, a
  communication graph, transactional case memory, and each agent's schema.
- **Local, apples-to-apples AI:** Qwen3-30B via Ollama for agent cognition and
  extraction; all-MiniLM-L6-v2 embeddings (384-dim) on a local GPU. No cloud
  LLM — the intelligence is local; the *memory* is the differentiator.
- **AWS:** S3 for the raw corpus and case snapshots; the Cold Case demo
  dashboard is deployed on AWS (see the ColdCase repo for the live URL).
- **Blind evaluation:** ground truth for every agent is sealed in a `*_truth`
  schema the agent's DB role has no grant on — scoring only.

## CockroachDB tools used (≥2 required — we used four)

1. **Distributed Vector Indexing (C-SPANN)** — semantic recall over 500K+ email
   chunks and SEC filings; the backbone of every agent's search.
2. **Managed MCP Server** — judges interrogate the live case memory in plain
   English ("who's the top suspect and why?").
3. **ccloud CLI** — agent-triggered backups of case memory at session end.
4. **Agent Skills** — schema design, query tuning, and observability during build.

Plus the property no vector store has: **SERIALIZABLE / ACID** — proven by Hold
Firewall and the concurrent multi-agent write demo.

## AWS services used

- **Amazon S3** — corpus storage and case-snapshot archival.
- **AWS-hosted demo** — the functional suspect-board dashboard.

## Challenges we ran into

- **Making "entwined" real, not rhetorical.** It would have been easy to ship
  five separate demos. Instead we put every agent in one database and proved the
  entwinement with a single cross-schema query that reconstructs a person's case
  file — including the Fastow gap where the suite outperforms any single agent.
- **Proving memory changes outcomes, not just speed.** Each agent needed a clean
  ablation isolating persistence as the only variable, scored against sealed
  ground truth.
- **Concurrency correctness.** Five agents writing shared case memory at once can
  silently lose data under weak isolation; Hold Firewall turns that failure mode
  into a headline result (0 vs ~119).

## Accomplishments we're proud of

- One SQL statement, five agents, one database — the entwinement made literal.
- Five independent memory ablations, each with a real, defensible number.
- A blind investigation that rediscovers real convictions from raw documents.
- A local-only intelligence stack, so the database — not a frontier model — is
  demonstrably doing the differentiated work.

## What we learned

Agentic memory is a *database* problem, not a prompt problem. Vectors are
necessary but not sufficient: contradictions, gaps, timelines, and holds all
require transactional state, relationships, and consistency that a vector cache
cannot provide. CockroachDB's combination of vectors + graph-style joins +
SERIALIZABLE is exactly the shape of a case file.

## What's next

- Run the LLM extraction layers (built and unit-verified) to grow Chronicle's
  timeline, Witness's statements, and Gap Hunter's references directly from the
  raw corpus — staged behind local GPU availability.
- Surface the unified case file as a live panel in the dashboard.

## Links

- **Suite (this repo):** https://github.com/banksythequantLab/ediscovery-suite
- **Cold Case:** https://github.com/banksythequantLab/ColdCase ·
  **Chronicle:** https://github.com/banksythequantLab/Chronicle ·
  **Witness:** https://github.com/banksythequantLab/Witness ·
  **Gap Hunter:** https://github.com/banksythequantLab/GapHunter ·
  **Hold Firewall:** https://github.com/banksythequantLab/HoldFirewall
- **Demo dashboard + video:** see the Cold Case repo.

MIT licensed. One memory backbone. Five legal agents. **Entwined.**
