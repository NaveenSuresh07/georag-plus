from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from app.config import settings

app = FastAPI(title="GeoRAG+ API", version="0.1.0")

# Setup SQLAlchemy engine using your database configuration settings
engine = create_engine(settings.DATABASE_URL)

@app.get("/health")
def health():
    return "ok"

@app.get("/study-area/summary")
def get_study_area_summary():
    try:
        with engine.connect() as conn:
            # Query row counts or summary details of your spatial layers
            result = conn.execute(text("""
                SELECT 'study_area_buildings' AS table_name, count(*) AS count FROM study_area_buildings
                UNION ALL
                SELECT 'roads', count(*) FROM roads
                UNION ALL
                SELECT 'crz_zones', count(*) FROM crz_zones;
            """))
            summary = [{"table": row[0], "count": row[1]} for row in result]
            return {"status": "success", "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))