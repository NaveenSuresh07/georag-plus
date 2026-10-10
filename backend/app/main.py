from fastapi import FastAPI
from sqlalchemy import create_engine, text
from .config import settings

app = FastAPI(title="GeoRAG+ API")
engine = create_engine(settings.db_url)

@app.get("/health")
def health():
    with engine.connect() as conn:
        postgis = conn.execute(text("SELECT PostGIS_Version()")).scalar()
        vector = conn.execute(
            text("SELECT extversion FROM pg_extension WHERE extname='vector'")
        ).scalar()
    return {"status": "ok", "postgis": postgis, "pgvector": vector}