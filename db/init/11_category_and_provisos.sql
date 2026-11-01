-- 11_category_and_provisos.sql   (GeoRAG+ Batch 5)
-- Location in repo: db/init/11_category_and_provisos.sql
-- 1) KPBR Rule 3(5): the Government notifies each Village Panchayat as Category I or II, so the
--    category is a fact about the panchayat. We store it on the plot record.
-- 2) Table 4 and others have provisos ("can be reduced to 0.5 m if there is no opening"). We keep the
--    wording next to the number and show it when a check fails.
-- Idempotent: safe to run more than once.
ALTER TABLE cadastral_parcels ADD COLUMN IF NOT EXISTS panchayat_category VARCHAR(2);   -- 'I' | 'II' | NULL = not set
ALTER TABLE rule_params       ADD COLUMN IF NOT EXISTS proviso TEXT;