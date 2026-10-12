-- Create a study area table clipped from the bulk-imported multipolygons table
DROP TABLE IF EXISTS study_area_buildings;

CREATE TABLE study_area_buildings AS
SELECT 
    osm_id,
    name,
    building,
    wkb_geometry AS geom
FROM multipolygons
WHERE (building IS NOT NULL)
  AND ST_Intersects(
      wkb_geometry,
      ST_MakeEnvelope(76.8, 8.4, 77.2, 8.7, 4326)
  );

-- Create a spatial index for high-performance GeoRAG queries
CREATE INDEX idx_study_area_buildings_geom ON study_area_buildings USING GIST (geom);