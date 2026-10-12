-- 04_batch3_schema.sql   (GeoRAG+ Batch 3)
-- Location in repo: db/init/04_batch3_schema.sql
-- Idempotent: safe to run more than once, and safe even if an earlier
-- migration (03) was never applied.

CREATE TABLE IF NOT EXISTS study_area (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    local_body_type VARCHAR(20),          -- panchayat | municipality | corporation
    geom GEOMETRY(Polygon, 4326)
);

CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now(),
    phase INT,
    parcel_id INT,
    check_name VARCHAR(80),
    verdict VARCHAR(20),                  -- PASS | FAIL | WARN | INFO
    inputs JSONB,
    cited_clauses JSONB,
    details TEXT
);

-- Columns used by the roads / utility loaders
ALTER TABLE roads ADD COLUMN IF NOT EXISTS osm_id BIGINT;
ALTER TABLE roads ADD COLUMN IF NOT EXISTS osm_highway VARCHAR(30);
ALTER TABLE roads ADD COLUMN IF NOT EXISTS source VARCHAR(20) DEFAULT 'mock';
ALTER TABLE utility_assets ADD COLUMN IF NOT EXISTS osm_id BIGINT;
ALTER TABLE utility_assets ADD COLUMN IF NOT EXISTS source VARCHAR(20) DEFAULT 'mock';

-- Parcels
ALTER TABLE cadastral_parcels ADD COLUMN IF NOT EXISTS local_body_type VARCHAR(20) DEFAULT 'panchayat';
ALTER TABLE cadastral_parcels ADD COLUMN IF NOT EXISTS village VARCHAR(80);
ALTER TABLE cadastral_parcels ADD COLUMN IF NOT EXISTS area_sqm NUMERIC;
ALTER TABLE cadastral_parcels ADD COLUMN IF NOT EXISTS source VARCHAR(20) DEFAULT 'mock';

-- Paddy Data Bank
ALTER TABLE paddy_data_bank ADD COLUMN IF NOT EXISTS source VARCHAR(30) DEFAULT 'mock';

-- Mock Encumbrance Certificate records (stand-in for PEARL)
CREATE TABLE IF NOT EXISTS ec_records (
    id SERIAL PRIMARY KEY,
    parcel_id INT REFERENCES cadastral_parcels(parcel_id) ON DELETE CASCADE,
    survey_no VARCHAR(50),
    thandaper_no VARCHAR(50),
    doc_no VARCHAR(30),
    doc_type VARCHAR(20),                 -- Sale | Mortgage | Release
    doc_date DATE,
    party_from TEXT,
    party_to TEXT,
    source VARCHAR(20) DEFAULT 'mock'
);
CREATE INDEX IF NOT EXISTS ec_parcel_idx ON ec_records (parcel_id);

-- Fees and tax rates live in the DB, not in code, with a "verified" flag.
-- Values below are PLACEHOLDERS from memory. Check them against the current
-- official notifications, then set verified = TRUE (see implementation.md, Section 4).
CREATE TABLE IF NOT EXISTS fee_rates (
    code VARCHAR(40) PRIMARY KEY,
    description TEXT,
    rate NUMERIC NOT NULL,
    effective_from DATE,
    source_note TEXT,
    verified BOOLEAN DEFAULT FALSE
);

INSERT INTO fee_rates (code, description, rate, source_note, verified) VALUES
 ('stamp_duty_pct',       'Stamp duty on conveyance (percent)',         8,       'PLACEHOLDER: verify against current Kerala notification', FALSE),
 ('registration_fee_pct', 'Registration fee (percent)',                 2,       'PLACEHOLDER: verify against current Kerala notification', FALSE),
 ('tds_194ia_pct',        'TDS rate under Section 194-IA (percent)',    1,       'PLACEHOLDER: verify (used in Batch 6)',                   FALSE),
 ('tds_194ia_threshold',  'Section 194-IA threshold (INR)',             5000000, 'PLACEHOLDER: verify (used in Batch 6)',                   FALSE)
ON CONFLICT (code) DO NOTHING;