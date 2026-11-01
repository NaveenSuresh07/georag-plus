from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from app.config import settings
from .phase1 import router as phase1_router
from .rag import router as rag_router
from .phase2 import router as phase2_router
from .phase3 import router as phase3_router
from .agent import router as agent_router
from .study_area import router as study_area_router

app = FastAPI(
    title="GeoRAG+ API",
    version="0.2.0",
    description="Automated Land Due Diligence, Building Rules Compliance, and Property Selling Verification Assistant for Kerala",
)

# Enable CORS for frontend Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(study_area_router)
app.include_router(phase1_router)
app.include_router(phase2_router)
app.include_router(phase3_router)
app.include_router(agent_router)
app.include_router(rag_router)

engine = create_engine(settings.DATABASE_URL)

@app.get("/health")
def health():
    return "ok"

    
