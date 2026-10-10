-- Your tables from the plan, plus the layers Phase 1/2 queries need
CREATE TABLE cadastral_parcels (
    parcel_id SERIAL PRIMARY KEY,
    survey_no VARCHAR(50),
    thandaper_no VARCHAR(50),
    land_type VARCHAR(30),            -- 'Purayidom', 'Nilam/Nanja'
    data_bank_status BOOLEAN DEFAULT FALSE,
    fair_value_per_are NUMERIC,
    geom GEOMETRY(Polygon, 4326)
);

CREATE TABLE utility_assets (
    asset_id SERIAL PRIMARY KEY,
    asset_type VARCHAR(30),           -- 'KSEB_HT_Line', 'KWA_Main', 'Transformer'
    voltage_kv INT,
    geom GEOMETRY(Geometry, 4326)
);

-- Referenced by your Step 1.2 query but missing from the original schema
CREATE TABLE paddy_data_bank (
    id SERIAL PRIMARY KEY,
    village VARCHAR(80),
    geom GEOMETRY(MultiPolygon, 4326)
);

CREATE TABLE roads (
    road_id SERIAL PRIMARY KEY,
    name VARCHAR(120),
    road_class VARCHAR(30),           -- 'NH', 'SH', 'MDR', 'Local'
    geom GEOMETRY(LineString, 4326)
);

CREATE TABLE crz_zones (
    id SERIAL PRIMARY KEY,
    crz_class VARCHAR(10),            -- 'CRZ-I', 'CRZ-II', ...
    geom GEOMETRY(MultiPolygon, 4326)
);

-- Statutory text chunks for RAG (384 dims = all-MiniLM-L6-v2)
CREATE TABLE regulation_chunks (
    chunk_id SERIAL PRIMARY KEY,
    source_doc VARCHAR(120),          -- 'KPBR 2019', 'KMBR 1999', ...
    clause_ref VARCHAR(60),           -- 'Rule 24(3)'
    content TEXT,
    embedding VECTOR(384)
);

CREATE INDEX parcel_spatial_idx  ON cadastral_parcels USING GIST (geom);
CREATE INDEX utility_spatial_idx ON utility_assets    USING GIST (geom);
CREATE INDEX paddy_spatial_idx   ON paddy_data_bank   USING GIST (geom);
CREATE INDEX roads_spatial_idx   ON roads             USING GIST (geom);
CREATE INDEX crz_spatial_idx     ON crz_zones         USING GIST (geom);
CREATE INDEX reg_embed_idx ON regulation_chunks USING hnsw (embedding vector_cosine_ops);