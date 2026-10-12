-- 05_mock_data.sql   (GeoRAG+ Batch 3)
-- Location in repo: db/scripts/05_mock_data.sql
-- Run AFTER 04_batch3_schema.sql.
-- Needs: study_area_buildings (your Batch 2 table) and public.multipolygons.
-- Safe to re-run: only rows with source = 'mock' / 'osm' are rebuilt.
-- EVERYTHING GENERATED HERE IS SYNTHETIC. Say so in the report.

BEGIN;

-- 1. MICRO-STUDY WARD ------------------------------------------------------
-- EDIT: ST_MakeEnvelope(west, south, east, north, 4326)  (about 1 km x 1 km)
-- Pick a spot that has plenty of buildings in study_area_buildings.
DELETE FROM study_area;
INSERT INTO study_area (name, local_body_type, geom)
VALUES ('Attingal Study Ward', 'panchayat',
        ST_MakeEnvelope(76.810, 8.690, 76.819, 8.699, 4326));

-- 2. PADDY DATA BANK (proxy) -----------------------------------------------
-- Real Data Bank maps need georeferencing in QGIS (later). For now: use OSM
-- farmland / meadow / wetland polygons as a stand-in.
DELETE FROM paddy_data_bank WHERE source = 'mock';
INSERT INTO paddy_data_bank (village, geom, source)
SELECT 'OSM proxy',
       ST_Multi(ST_CollectionExtract(ST_MakeValid(m.wkb_geometry), 3)),
       'mock'
FROM multipolygons m, study_area s
WHERE (m.landuse IN ('farmland', 'meadow') OR m."natural" = 'wetland')
  AND m.building IS NULL
  AND ST_Intersects(m.wkb_geometry, s.geom);

-- Fallback: if OSM has nothing here, draw two synthetic Data Bank blocks
DO $$
BEGIN
  IF (SELECT count(*) FROM paddy_data_bank WHERE source = 'mock') = 0 THEN
    INSERT INTO paddy_data_bank (village, geom, source) VALUES
     ('Synthetic block A', ST_Multi(ST_MakeEnvelope(76.8145, 8.6900, 76.8190, 8.6935, 4326)), 'mock'),
     ('Synthetic block B', ST_Multi(ST_MakeEnvelope(76.8100, 8.6955, 76.8125, 8.6980, 4326)), 'mock');
    RAISE NOTICE 'No OSM farmland/wetland in ward: inserted 2 synthetic Data Bank blocks';
  END IF;
END $$;

-- 3. MOCK CADASTRAL PARCELS ------------------------------------------------
-- One lot per building: Voronoi cell around each building, limited to an
-- 18 m ring around the building and to the ward. Realistic enough for demos.
DELETE FROM ec_records;
DELETE FROM cadastral_parcels WHERE source = 'mock';

WITH ward AS (
  SELECT geom FROM study_area ORDER BY id LIMIT 1
),
bld AS (
  SELECT row_number() OVER () AS rn,
         sb.geom AS bgeom,
         ST_PointOnSurface(sb.geom) AS pt
  FROM study_area_buildings sb, ward w
  WHERE ST_Intersects(sb.geom, w.geom)
    AND ST_Area(sb.geom::geography) >= 25            -- skip sheds / tiny objects
),
cells AS (
  SELECT (ST_Dump(
            ST_VoronoiPolygons((SELECT ST_Collect(pt) FROM bld), 0, (SELECT geom FROM ward))
         )).geom AS cell
),
lots AS (
  SELECT b.rn,
         ST_Intersection(
           ST_Intersection(c.cell, ST_Buffer(b.bgeom::geography, 18)::geometry),
           (SELECT geom FROM ward)
         ) AS lot
  FROM bld b JOIN cells c ON ST_Contains(c.cell, b.pt)
),
parts AS (
  SELECT rn, (ST_Dump(ST_CollectionExtract(ST_MakeValid(lot), 3))).geom AS part
  FROM lots
),
best AS (
  SELECT DISTINCT ON (rn) rn, part
  FROM parts
  ORDER BY rn, ST_Area(part) DESC
),
numbered AS (
  SELECT part,
         row_number() OVER (ORDER BY ST_X(ST_Centroid(part)), ST_Y(ST_Centroid(part))) AS seq
  FROM best
  WHERE ST_Area(part::geography) >= 40
)
INSERT INTO cadastral_parcels
  (survey_no, thandaper_no, land_type, data_bank_status, fair_value_per_are,
   geom, local_body_type, village, area_sqm, source)
SELECT (100 + seq / 6)::text || '/' || (1 + seq % 6)::text,
       'T-' || (2000 + seq)::text,
       'Purayidom',
       FALSE,
       250000 + (seq % 7) * 50000,                   -- MOCK fair value per Are
       part,
       (SELECT local_body_type FROM study_area ORDER BY id LIMIT 1),
       (SELECT name FROM study_area ORDER BY id LIMIT 1),
       ST_Area(part::geography),
       'mock'
FROM numbered;

-- 4. DATA BANK FLAGS + PLANTED TEST CASES ----------------------------------
UPDATE cadastral_parcels p
SET data_bank_status = TRUE
WHERE p.source = 'mock'
  AND EXISTS (SELECT 1 FROM paddy_data_bank d WHERE ST_Intersects(p.geom, d.geom));

-- Land type "as recorded in ReLIS": consistent with the Data Bank...
UPDATE cadastral_parcels
SET land_type = CASE WHEN data_bank_status THEN 'Nilam/Nanja' ELSE 'Purayidom' END
WHERE source = 'mock';

-- ...except every 10th Data Bank parcel, recorded as Purayidom (record conflict)
UPDATE cadastral_parcels
SET land_type = 'Purayidom'
WHERE source = 'mock' AND data_bank_status AND parcel_id % 10 = 0;

-- 5. MOCK EC RECORDS -------------------------------------------------------
-- Every parcel: one original sale
INSERT INTO ec_records (parcel_id, survey_no, thandaper_no, doc_no, doc_type, doc_date, party_from, party_to)
SELECT parcel_id, survey_no, thandaper_no,
       (1000 + parcel_id)::text || '/' || (1995 + parcel_id % 25)::text,
       'Sale',
       make_date(1995 + parcel_id % 25, 1 + parcel_id % 12, 1 + parcel_id % 28),
       'Previous Owner ' || parcel_id, 'Owner ' || parcel_id
FROM cadastral_parcels WHERE source = 'mock';

-- 20% also have a mortgage
INSERT INTO ec_records (parcel_id, survey_no, thandaper_no, doc_no, doc_type, doc_date, party_from, party_to)
SELECT parcel_id, survey_no, thandaper_no,
       (5000 + parcel_id)::text || '/' || (2005 + parcel_id % 15)::text,
       'Mortgage',
       make_date(2005 + parcel_id % 15, 1 + parcel_id % 12, 1 + parcel_id % 28),
       'Owner ' || parcel_id, 'Mock Bank ' || (parcel_id % 4)
FROM cadastral_parcels WHERE source = 'mock' AND parcel_id % 5 = 0;

-- Half of those are released; the rest stay OPEN (planted FAIL cases)
INSERT INTO ec_records (parcel_id, survey_no, thandaper_no, doc_no, doc_type, doc_date, party_from, party_to)
SELECT parcel_id, survey_no, thandaper_no,
       (8000 + parcel_id)::text || '/' || (2007 + parcel_id % 15)::text,
       'Release',
       make_date(2007 + parcel_id % 15, 1 + parcel_id % 12, 1 + parcel_id % 28),
       'Mock Bank ' || (parcel_id % 4), 'Owner ' || parcel_id
FROM cadastral_parcels WHERE source = 'mock' AND parcel_id % 10 = 0;

-- 6. ROADS from the OSM lines layer (fixes "roads = 0") --------------------
DO $$
DECLARE
  tbl regclass := COALESCE(to_regclass('public.lines'), to_regclass('osm_raw.lines'));
BEGIN
  IF tbl IS NULL THEN
    RAISE NOTICE 'lines table not found: roads skipped (import the OSM lines layer first)';
  ELSE
    DELETE FROM roads WHERE source = 'osm';
    EXECUTE format($q$
      INSERT INTO roads (osm_id, name, road_class, osm_highway, source, geom)
      SELECT l.osm_id::bigint,
             LEFT(l.name, 120),
             CASE WHEN l.other_tags::text ~ '"ref"=>"NH' THEN 'NH'
                  WHEN l.other_tags::text ~ '"ref"=>"SH' THEN 'SH'
                  ELSE 'Local' END,
             LEFT(l.highway, 30),
             'osm',
             l.wkb_geometry
      FROM %s l
      WHERE l.highway IS NOT NULL
        AND ST_Intersects(
              l.wkb_geometry,
              ST_Buffer((SELECT geom FROM study_area ORDER BY id LIMIT 1)::geography, 1500)::geometry)
    $q$, tbl);
  END IF;
END $$;

COMMIT;
ANALYZE;

-- 7. REPORT ----------------------------------------------------------------
SELECT 'ward area (sq km)' AS item,
       round((ST_Area(geom::geography) / 1000000)::numeric, 2)::text AS value
FROM study_area
UNION ALL SELECT 'mock parcels',
       count(*)::text FROM cadastral_parcels WHERE source = 'mock'
UNION ALL SELECT 'parcels in Data Bank',
       count(*)::text FROM cadastral_parcels WHERE source = 'mock' AND data_bank_status
UNION ALL SELECT 'record conflicts (Purayidom but in Data Bank)',
       count(*)::text FROM cadastral_parcels
       WHERE source = 'mock' AND data_bank_status AND land_type = 'Purayidom'
UNION ALL SELECT 'parcels with an open mortgage',
       count(*)::text FROM (
         SELECT parcel_id FROM ec_records GROUP BY parcel_id
         HAVING sum((doc_type = 'Mortgage')::int) > sum((doc_type = 'Release')::int)) x
UNION ALL SELECT 'Data Bank polygons',
       count(*)::text FROM paddy_data_bank WHERE source = 'mock'
UNION ALL SELECT 'roads (osm)',
       count(*)::text FROM roads WHERE source = 'osm';