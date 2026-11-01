-- 10_rule_params_category.sql   (GeoRAG+ Batch 5)
-- Location in repo: db/init/10_rule_params_category.sql
-- Table 6 has Category I and Category II values for coverage and FAR per panchayat.
ALTER TABLE rule_params ADD COLUMN IF NOT EXISTS category VARCHAR(10);
