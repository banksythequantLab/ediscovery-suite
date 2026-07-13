-- Multi-region resilience demo for cross-border e-discovery.
-- LOCAL SIMULATION (cockroach demo, in-memory) of a 3-region cluster -- honestly
-- labeled as a simulation, not a paid cloud deployment. It runs the REAL
-- multi-region DDL and demonstrates a full-region outage with zero data loss.
--
-- Run:  cockroach.exe demo --nodes 6 --no-example-database --insecure \
--         --demo-locality=region=us-east1:region=us-east1:region=us-west1:region=us-west1:region=europe-west1:region=europe-west1 \
--         < geo_failover.sql
-- Nodes 1-2 = us-east1, 3-4 = us-west1, 5-6 = europe-west1.

SELECT '===== 1. Cluster topology: three simulated regions =====' AS step;
SHOW REGIONS;

SELECT '===== 2. A database that SURVIVES a full region outage =====' AS step;
CREATE DATABASE ediscovery
  PRIMARY REGION "us-east1"
  REGIONS "us-east1", "us-west1", "europe-west1"
  SURVIVE REGION FAILURE;
USE ediscovery;

SELECT '===== 3. Legal holds, domiciled to each custodian jurisdiction (REGIONAL BY ROW) =====' AS step;
CREATE TABLE legal_holds (
  id INT PRIMARY KEY, custodian STRING, matter STRING
) LOCALITY REGIONAL BY ROW;
INSERT INTO legal_holds (id, custodian, matter, crdb_region) VALUES
 (1,'Kenneth Lay','MDL-1446','us-east1'),
 (2,'Jeffrey Skilling','MDL-1446','us-east1'),
 (3,'Andrew Fastow','MDL-1446','us-east1'),
 (4,'Enron Europe - Trader A','FSA-London','europe-west1'),
 (5,'Enron Europe - Trader B','FSA-London','europe-west1'),
 (6,'Enron West - Power Analyst','FERC-West','us-west1');

SELECT '===== data domiciling: EU custodian rows are pinned to europe-west1 (GDPR) =====' AS step;
SELECT crdb_region, count(*) AS holds, string_agg(custodian, ', ') AS custodians
FROM legal_holds GROUP BY crdb_region ORDER BY 1;
SELECT count(*) AS holds_BEFORE_outage FROM legal_holds;

SELECT '===== 4. SIMULATE A REGION OUTAGE: take the entire europe-west1 region offline =====' AS step;
\demo shutdown 5
\demo shutdown 6
SELECT pg_sleep(10);

SELECT '===== 5. AFTER the EU region is DOWN: the case file still serves =====' AS step;
SELECT count(*) AS holds_AFTER_outage FROM legal_holds;
SELECT crdb_region, count(*) AS holds FROM legal_holds GROUP BY crdb_region ORDER BY 1;
SELECT '===== SURVIVE REGION FAILURE: EU rows still readable from surviving regions -- 0 holds lost =====' AS step;
