import osmium
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import polygonize
from sqlalchemy import create_engine
import pandas as pd


# Define a custom Osmium handler to extract building geometries
class BuildingHandler(osmium.SimpleHandler):

  def __init__(self):
    super(BuildingHandler, self).__init__()
    self.buildings = []
    self.nodes = {}

  def node(self, n):
    # Store node coordinates for way assembly
    self.nodes[n.id] = (n.location.lon, n.location.lat)

  def way(self, w):
    # Check if the way has a building tag
    tags = {tag.k: tag.v for tag in w.tags}
    if "building" in tags:
      coords = [self.nodes[nd.ref] for nd in w.nodes if nd.ref in self.nodes]
      if len(coords) >= 3:  # Valid polygon needs at least 3 points
        try:
          poly = Polygon(coords)
          if poly.is_valid:
            self.buildings.append({
                "osm_id": w.id,
                "building": tags["building"],
                "name": tags.get("name"),
                "geom": str(poly.wkt),  # Well-Known Text format for PostGIS
            })
        except Exception:
          pass


print("Parsing PBF file for buildings (this may take a minute)...")
handler = BuildingHandler()
handler.apply_file("southern-zone-261009.osm.pbf", locations=True)

df = pd.DataFrame(handler.buildings)
print(f"Extracted {len(df)} valid buildings.")

if not df.empty:
  # Connect to PostGIS database
  db_url = "postgresql://georag:georagpassword@localhost:5432/georag"
  engine = create_engine(db_url)

  # Insert data into PostgreSQL table
  df.to_sql(
      "osm_buildings",
      con=engine,
      if_exists="append",
      index=False,
      method="multi",
  )
  print("Data successfully inserted into PostGIS database!")
else:
  print("No buildings found in the extraction.")