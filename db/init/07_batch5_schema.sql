-- 07_batch5_schema.sql   (GeoRAG+ Batch 5)
-- Location in repo: db/init/07_batch5_schema.sql
-- Idempotent: safe to run more than once.

-- 1. RULE VALUES TYPED IN FROM THE PDFs ------------------------------------------------
-- One row = one number from a rule table, plus the conditions it applies under.
-- The rule engine reads THIS table (never numbers guessed from retrieved text) and quotes
-- the exact clause (doc_code + clause_ref) as its source.
--
-- Range convention (write it the way the rule is worded):
--   *_min is EXCLUSIVE ("exceeding 7 m"),  *_max is INCLUSIVE ("up to 10 m").
--   "up to 7 m"            -> height_max_m = 7
--   "exceeding 7, up to 10" -> height_min_m = 7, height_max_m = 10
--   "not less than 300 m2"  -> plot_min_sqm = 299.99
--   Built-up area (total floor area of the building) works the same way: builtup_min_sqm / builtup_max_sqm.
--   KPBR Table 4 is organised by occupancy group + built-up area, so this condition is needed.
CREATE TABLE IF NOT EXISTS rule_params (
    id SERIAL PRIMARY KEY,
    doc_code     VARCHAR(30) NOT NULL,     -- KPBR | KMBR
    clause_ref   VARCHAR(60) NOT NULL,     -- must match regulation_chunks.clause_ref, e.g. 'Rule 26'
    table_ref    VARCHAR(60),              -- e.g. 'Table 4'
    use_group    VARCHAR(10),              -- occupancy group: 'A1' = residential; NULL = any
    param        VARCHAR(60) NOT NULL,     -- see the list in load_rule_params.py
    height_min_m NUMERIC,
    height_max_m NUMERIC,
    plot_min_sqm NUMERIC,
    plot_max_sqm NUMERIC,
    builtup_min_sqm NUMERIC,
    builtup_max_sqm NUMERIC,
    road_class   VARCHAR(20),              -- NH | SH | MDR | Local ; NULL = any
    value        NUMERIC NOT NULL,
    unit         VARCHAR(20),
    verified     BOOLEAN DEFAULT FALSE,    -- TRUE only after you checked the number against the PDF
    note         TEXT,
    source       VARCHAR(20) DEFAULT 'csv'
);
CREATE INDEX IF NOT EXISTS rule_params_lookup_idx ON rule_params (doc_code, param);

-- 2. AREAS WITH SPECIAL DISTANCE RULES (CRZ, railway, airport ...) ---------------------
-- Empty by default. Load real or mock polygons/lines here and add a matching
-- 'min_distance_<ZONE_TYPE>' row to rule_params to switch the check on.
CREATE TABLE IF NOT EXISTS restricted_zones (
    id SERIAL PRIMARY KEY,
    zone_type VARCHAR(30) NOT NULL,        -- 'CRZ' | 'RAILWAY' | 'AIRPORT' ...
    name TEXT,
    source VARCHAR(20) DEFAULT 'mock',
    geom GEOMETRY(Geometry, 4326)
);
CREATE INDEX IF NOT EXISTS restricted_zones_geom_idx ON restricted_zones USING GIST (geom);

-- 3. CONSTRUCTION WORKERS WELFARE CESS (placeholders: verify before any demo) ----------
INSERT INTO fee_rates (code, description, rate, source_note, verified) VALUES
 ('bocw_cess_pct',           'Construction workers welfare cess (percent of construction cost)', 1,   'PLACEHOLDER: verify against the current Kerala notification', FALSE),
 ('bocw_cess_threshold_sqm', 'Built-up area above which the cess applies (sq m)',               100, 'PLACEHOLDER: verify against the current Kerala notification', FALSE)
ON CONFLICT (code) DO NOTHING;