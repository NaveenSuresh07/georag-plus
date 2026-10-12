import osmium
from shapely.geometry import Polygon
from sqlalchemy import create_engine
import pandas as pd


# Bounding box for your area of interest (e.g., Thiruvananthapuram region)
# Format: (min_lon, min_lat, max_lon, max_lat)
MIN_LON, MIN_LAT, MAX_LON, MAX_LAT = 76.8, 8.4, 77.2, 8.7


class BBoxHandler(osmium.SimpleHandler):

  def __init__(self):
    super().__init__()
    self.buildings = []
    self.nodes = {}

  def node(self, n):
    self.nodes[n.id] = (n.location.lon, n.location.lat)

  def way(self, w):
    tags = {tag.k: tag.v for tag in w.tags}
    if "building" in tags:
      coords = [
          self.nodes[nd.ref] for nd in w.nodes if nd.ref in self.nodes
      ]
      if len(coords) >= 3:
        # Check if any point falls inside our bounding box
        if any(
            MIN_LON <= lon <= MAX_LON and MIN_LAT <= lat <= MAX_LAT
            for lon, lat in coords
        ):
          try:
            poly = Polygon(coords)
            if poly.is_valid:
              self.buildings.append({
                  "osm_id": w.id,
                  "building": tags["building"],
                  "name": tags.get("name"),
                  "geom": str(poly.wkt),
              })
          except Exception:
            pass


print("Clipping and extracting buildings for your target area...")
handler = BBoxHandler()
handler.apply_file("southern-zone-261009.osm.pbf", locations=True)

df = pd.DataFrame(handler.buildings)
print(f"Extracted {len(df)} buildings within the bounding box.")

if not df.empty:
# Change this line in clip.py:
db_url = "postgresql+psycopg2://georag:georagpassword@localhost:5432/georag"
  engine = create_engine(db_url)
  df.to_sql(
      "osm_buildings",
      con=engine,
      if_exists="append",
      index=False,
      method="multi",
  )
  print("Successfully inserted clipped buildings into PostGIS!")
else:
  print("No buildings found in this bounding box.")