-- Multi-region data domiciling for cross-border e-discovery.
-- Run on a (simulated) multi-region CockroachDB cluster:
--   cockroach demo --nodes 3 --no-example-database --insecure \
--     --demo-locality=region=us-east1:region=us-west1:region=europe-west1 \
--     < geo_partition.sql
-- Enron records span jurisdictions (Houston HQ, London trading desk). GDPR /
-- data-sovereignty law forbids EU custodian data from leaving the EU. Here the
-- DATABASE -- not application code -- pins each row to its legal region.

SELECT '=== 1. The cluster is multi-region ===' AS step;
SHOW REGIONS;

SELECT '=== 2. A database that SURVIVES a full region outage ===' AS step;
CREATE DATABASE ediscovery
  PRIMARY REGION "us-east1"
  REGIONS "us-east1", "us-west1", "europe-west1"
  SURVIVE REGION FAILURE;
USE ediscovery;

SELECT '=== 3. Custodian docs are REGIONAL BY ROW (row-level domiciling) ===' AS step;
CREATE TABLE custodians (
  id INT PRIMARY KEY, name STRING, office STRING, role STRING
) LOCALITY REGIONAL BY ROW;

SELECT '=== 4. Pin each custodian to their legal jurisdiction ===' AS step;
INSERT INTO custodians (id, name, office, role, crdb_region) VALUES
 (1,'Kenneth Lay','Houston','Chairman','us-east1'),
 (2,'Jeffrey Skilling','Houston','CEO','us-east1'),
 (3,'Andrew Fastow','Houston','CFO','us-east1'),
 (4,'Enron Europe - Trader A','London','Trading','europe-west1'),
 (5,'Enron Europe - Trader B','London','Trading','europe-west1'),
 (6,'Enron West - Power Analyst','Portland','Power','us-west1');

SELECT '=== 5. Data domiciling: rows live in the region of their jurisdiction ===' AS step;
SELECT crdb_region, count(*) AS docs, string_agg(name, ', ') AS custodians
FROM custodians GROUP BY crdb_region ORDER BY 1;

SELECT '=== 6. EU custodians (GDPR) are pinned to europe-west1 ===' AS step;
SELECT name, office, crdb_region FROM custodians WHERE crdb_region = 'europe-west1';

SELECT '=== 7. The multi-region config the database enforces ===' AS step;
SHOW CREATE TABLE custodians;
