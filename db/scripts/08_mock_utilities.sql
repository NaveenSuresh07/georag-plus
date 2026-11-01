-- 08_mock_utilities.sql   (GeoRAG+ Batch 5, OPTIONAL)
-- Location in repo: db/scripts/08_mock_utilities.sql
-- OpenStreetMap has almost no water or electricity data for rural Kerala, so this adds
-- SYNTHETIC assets near the study ward so the utility checks have something to measure:
--   * KWA water mains that follow the roads
--   * KSEB transformers at the middle of the six longest roads
-- Needs the roads table to be filled (Batch 3 script, section 6).
-- Everything here is fake: say so in the report. Safe to re-run (only touches source = 'mock').

BEGIN;

DELETE FROM utility_assets WHERE source = 'mock';

INSERT INTO utility_assets (asset_type, source, geom)
SELECT 'KWA_Main', 'mock', r.geom
FROM roads r, study_area s
WHERE ST_DWithin(r.geom::geography, s.geom::geography, 200)
  AND ST_GeometryType(r.geom) = 'ST_LineString';

INSERT INTO utility_assets (asset_type, voltage_kv, source, geom)
SELECT 'Transformer', 11, 'mock', ST_LineInterpolatePoint(x.geom, 0.5)
FROM (
  SELECT r.geom
  FROM roads r, study_area s
  WHERE ST_DWithin(r.geom::geography, s.geom::geography, 300)
    AND ST_GeometryType(r.geom) = 'ST_LineString'
  ORDER BY ST_Length(r.geom::geography) DESC
  LIMIT 6
) x;

COMMIT;

SELECT asset_type, source, count(*) AS rows FROM utility_assets GROUP BY 1, 2 ORDER BY 1, 2;