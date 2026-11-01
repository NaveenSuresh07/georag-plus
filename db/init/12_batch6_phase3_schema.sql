-- 12_batch6_phase3_schema.sql   (GeoRAG+ Batch 6: Phase 3 Selling & Compliance)
-- Location in repo: db/init/12_batch6_phase3_schema.sql
-- Idempotent: safe to run more than once.

-- 1. PROPERTY ASSESSMENTS & OCCUPANCY CERTIFICATES (Local Body Sanchaya Stand-in)
CREATE TABLE IF NOT EXISTS property_assessments (
    id SERIAL PRIMARY KEY,
    parcel_id INT NOT NULL REFERENCES cadastral_parcels(parcel_id) ON DELETE CASCADE,
    door_no VARCHAR(50),                         -- e.g. '12/450' or 'UA-12/450'
    occupancy_certificate_no VARCHAR(50),        -- e.g. 'OC/ATTL/2022/104'
    oc_issue_date DATE,
    assessment_year VARCHAR(10) DEFAULT '2025-26',
    annual_property_tax NUMERIC(10, 2) DEFAULT 2400.00,
    tax_arrears NUMERIC(10, 2) DEFAULT 0.00,
    status VARCHAR(30) NOT NULL DEFAULT 'AUTHORIZED', -- 'AUTHORIZED' | 'UNAUTHORIZED' | 'PENDING_OC' | 'NO_BUILDING'
    unauthorized_reason TEXT,
    source VARCHAR(20) DEFAULT 'mock'
);
CREATE INDEX IF NOT EXISTS prop_assess_parcel_idx ON property_assessments (parcel_id);

-- 2. CAPITAL GAINS & TDS TAX RATES (placeholders: verify before demo)
INSERT INTO fee_rates (code, description, rate, source_note, verified) VALUES
 ('ltcg_property_pct',      'Long term capital gains tax rate on immovable property (percent)', 12.5, 'Section 112 / Finance Act 2024: 12.5% without indexation', FALSE),
 ('ltcg_holding_months',    'Holding period threshold for long term property gains (months)',   24,   'Section 2(42A) of Income Tax Act: 24 months for immovable property', TRUE)
ON CONFLICT (code) DO NOTHING;

-- 3. MOCK ASSESSMENTS FOR ALL STUDY WARD PARCELS
DELETE FROM property_assessments WHERE source = 'mock';

INSERT INTO property_assessments
  (parcel_id, door_no, occupancy_certificate_no, oc_issue_date, annual_property_tax, tax_arrears, status, unauthorized_reason, source)
SELECT
    p.parcel_id,
    CASE
        WHEN p.parcel_id = 2 OR (p.parcel_id > 5 AND p.parcel_id % 25 = 0)
            THEN 'UA-12/' || (400 + p.parcel_id)::text
        WHEN p.parcel_id = 3 OR (p.parcel_id > 5 AND p.parcel_id % 40 = 0)
            THEN NULL
        WHEN p.parcel_id = 5
            THEN NULL
        ELSE 'Ward 12/' || (400 + p.parcel_id)::text
    END AS door_no,
    CASE
        WHEN p.parcel_id IN (2, 3, 5) OR (p.parcel_id > 5 AND (p.parcel_id % 25 = 0 OR p.parcel_id % 40 = 0))
            THEN NULL
        ELSE 'OC/ATTL/' || (2020 + (p.parcel_id % 5))::text || '/' || (1000 + p.parcel_id)::text
    END AS occupancy_certificate_no,
    CASE
        WHEN p.parcel_id IN (2, 3, 5) OR (p.parcel_id > 5 AND (p.parcel_id % 25 = 0 OR p.parcel_id % 40 = 0))
            THEN NULL
        ELSE (DATE '2021-01-15' + (p.parcel_id * 3)::int)
    END AS oc_issue_date,
    CASE
        WHEN p.parcel_id = 2 OR (p.parcel_id > 5 AND p.parcel_id % 25 = 0)
            THEN 5800.00   -- Punitive / double tax on unauthorized construction
        WHEN p.parcel_id = 5
            THEN 0.00      -- Vacant land
        ELSE 2400.00 + (p.parcel_id % 6) * 350.00
    END AS annual_property_tax,
    CASE
        WHEN p.parcel_id = 4 OR (p.parcel_id > 5 AND p.parcel_id % 30 = 0)
            THEN 14500.00  -- Arrears outstanding
        ELSE 0.00
    END AS tax_arrears,
    CASE
        WHEN p.parcel_id = 2 OR (p.parcel_id > 5 AND p.parcel_id % 25 = 0)
            THEN 'UNAUTHORIZED'
        WHEN p.parcel_id = 3 OR (p.parcel_id > 5 AND p.parcel_id % 40 = 0)
            THEN 'PENDING_OC'
        WHEN p.parcel_id = 5
            THEN 'NO_BUILDING'
        ELSE 'AUTHORIZED'
    END AS status,
    CASE
        WHEN p.parcel_id = 2 OR (p.parcel_id > 5 AND p.parcel_id % 25 = 0)
            THEN 'Deviation from approved plan: built beyond sanctioned coverage and without final occupancy clearance under KMBR Rule 20'
        WHEN p.parcel_id = 3 OR (p.parcel_id > 5 AND p.parcel_id % 40 = 0)
            THEN 'Construction completed; application for occupancy certificate pending verification under KMBR Rule 20(3)'
        ELSE NULL
    END AS unauthorized_reason,
    'mock'
FROM cadastral_parcels p;
