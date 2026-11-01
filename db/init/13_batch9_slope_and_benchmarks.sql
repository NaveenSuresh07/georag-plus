-- Batch 9 Migration: Terrain Elevation, Slope %, and Soil Stabilization Schema
-- Governing Code: KMBR 2019 Rule 26(4) / KPBR 2019 Rule 26 (Slopes exceeding 1:5 or 20% gradient)

ALTER TABLE cadastral_parcels
ADD COLUMN IF NOT EXISTS elevation_min_m NUMERIC(5,2) DEFAULT 18.00,
ADD COLUMN IF NOT EXISTS elevation_max_m NUMERIC(5,2) DEFAULT 22.00,
ADD COLUMN IF NOT EXISTS avg_slope_pct NUMERIC(5,2) DEFAULT 4.50,
ADD COLUMN IF NOT EXISTS has_retaining_wall BOOLEAN DEFAULT false;

-- Populate realistic undulating terrain for Attingal Municipality (elevations 14m - 32m MSL)
UPDATE cadastral_parcels
SET 
    elevation_min_m = ROUND((15.0 + (parcel_id % 11) * 1.2)::numeric, 2),
    elevation_max_m = ROUND((18.0 + (parcel_id % 11) * 1.2 + (parcel_id % 5) * 0.8)::numeric, 2),
    avg_slope_pct = ROUND((2.5 + (parcel_id % 9) * 1.2)::numeric, 2),
    has_retaining_wall = false;

-- Specific Benchmark Plots for Slope Testing:
-- Plot #42: Steep hillside without retaining wall (FAIL under KMBR Rule 26(4))
UPDATE cadastral_parcels
SET 
    elevation_min_m = 14.50,
    elevation_max_m = 28.80,
    avg_slope_pct = 24.50,
    has_retaining_wall = false
WHERE parcel_id = 42;

-- Plot #43: Steep hillside WITH certified retaining wall (WARN under KMBR Rule 26(4))
UPDATE cadastral_parcels
SET 
    elevation_min_m = 16.00,
    elevation_max_m = 29.50,
    avg_slope_pct = 22.80,
    has_retaining_wall = true
WHERE parcel_id = 43;

-- Plot #30 and Plot #50: Small plots (<= 125 sqm) with gentle slope
UPDATE cadastral_parcels
SET 
    geom = ST_Affine(geom, 0.5, 0, 0, 0.5, ST_X(ST_Centroid(geom)) * 0.5, ST_Y(ST_Centroid(geom)) * 0.5),
    area_sqm = 114.84,
    avg_slope_pct = 3.20
WHERE parcel_id = 30;

UPDATE cadastral_parcels
SET 
    geom = ST_Affine(geom, 0.47, 0, 0, 0.47, ST_X(ST_Centroid(geom)) * 0.53, ST_Y(ST_Centroid(geom)) * 0.53),
    area_sqm = 112.02,
    avg_slope_pct = 3.20
WHERE parcel_id = 50;

-- Ensure clean assessment statuses for dedicated benchmark test parcels
UPDATE property_assessments
SET tax_arrears = 0.00, status = 'AUTHORIZED', door_no = 'Ward 12/430'
WHERE parcel_id = 30;

UPDATE property_assessments
SET tax_arrears = 0.00, status = 'AUTHORIZED', door_no = 'Ward 12/450'
WHERE parcel_id = 50;

UPDATE property_assessments
SET tax_arrears = 0.00, status = 'AUTHORIZED', door_no = 'Ward 12/500'
WHERE parcel_id = 100;

-- Ensure Plot 10 overlaps Paddy Data Bank (Record Conflict benchmark: Purayidom in record, but in Data Bank)
INSERT INTO paddy_data_bank (village, geom, source)
SELECT 'Attingal', ST_Multi(ST_Buffer(ST_Centroid(geom), 0.0001)), 'mock'
FROM cadastral_parcels
WHERE parcel_id = 10
  AND NOT EXISTS (
      SELECT 1 FROM paddy_data_bank d, cadastral_parcels p
      WHERE p.parcel_id = 10 AND ST_Intersects(p.geom, d.geom)
  );

