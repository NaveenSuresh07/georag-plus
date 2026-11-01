-- 09_builtup_columns.sql   (GeoRAG+ Batch 5 fix)
-- Location in repo: db/init/09_builtup_columns.sql
-- For databases where 07_batch5_schema.sql was ALREADY applied: adds the built-up area conditions
-- (KPBR Table 4 depends on built-up area). Idempotent: safe to run more than once.
ALTER TABLE rule_params ADD COLUMN IF NOT EXISTS builtup_min_sqm NUMERIC;   -- exclusive lower bound
ALTER TABLE rule_params ADD COLUMN IF NOT EXISTS builtup_max_sqm NUMERIC;   -- inclusive upper bound