# GeoRAG+: Agentic Geospatial RAG & Smart Governance Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.4-green.svg)](https://postgis.net/)
[![pgvector](https://img.shields.io/badge/pgvector-HNSW-blueviolet.svg)](https://github.com/pgvector/pgvector)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9-brightgreen.svg)](https://leafletjs.com/)
[![Tests](https://img.shields.io/badge/Tests-69%20Passing-success.svg)](backend/tests/)
[![Milestone](https://img.shields.io/badge/Status-Batches%201--9%20Completed-brightgreen.svg)](docs/implementation.md)

> **An Agentic Multi-Modal Geospatial RAG System for Autonomous Terrain Analysis, Hydrodynamic Simulation, and Smart Governance**  
> *Target Study Area:* Attingal Municipality Ward (Thiruvananthapuram District, Kerala, India)

---

## 📌 Overview & Core Invariants

Traditional GIS tools (e.g., ArcGIS, QGIS) require specialized training, have prohibitive licensing costs, and operate completely isolated from statutory regulatory databases. Meanwhile, standard LLM chatbots suffer from **catastrophic spatial hallucinations**—inventing cadastral parcel boundaries, hallucinating setbacks, and failing at metric planar coordinates.

**GeoRAG+** solves this by enforcing a strict architectural invariant:

> 🛡️ **Invariant: Strict Decoupling of Cognition and Computation**  
> *The computer computes; the LLM only orchestrates, explains, and cites.*  
> Spatial math, setback buffers, slope analysis, and zoning queries are calculated strictly by **PostGIS (R-Tree indexed)**, **pgvector (HNSW indexed)**, and **NumPy / Shapely**. The LLM operates solely as a cognitive orchestrator and explainer, backed by statutory citations (KMBR 2019, KPBR 2019, Kerala Wetland Act 2008).

---

## 🗺️ Development Status & Roadmap

The architecture is divided into two major phases across 18 development batches (see [`docs/implementation.md`](docs/implementation.md) for full engineering specifications).

### Phase 1: Core Cadastral Engine & Governance AI (Batches 1 – 9) — **✅ 100% Complete & Verified**
* All core spatial pipelines, FastAPI services, React UI, and test suites are implemented and verified with **69/69 passing automated tests** across a curated 20-plot benchmark matrix.

| Batch | Module / Subsystem | Key Deliverables | Status |
| :--- | :--- | :--- | :---: |
| **Batch 1** | Spatial Database Foundation | Docker PostGIS 16 + pgvector, initial schema, health checks | ✅ Complete |
| **Batch 2** | OSM Ingestion & Invariant Guard | OSM ingestion via GDAL/ogr2ogr, bounding box clipping | ✅ Complete |
| **Batch 3** | Mock Parcels & Phase 1 Engine | Cadastral parcel seeding, statutory paddy/wetland compliance | ✅ Complete |
| **Batch 4** | Statute RAG Engine | HNSW pgvector indexing, verified legal sub-rule citations | ✅ Complete |
| **Batch 5** | Phase 2 Metric Setback Geometry | Planar CRS reprojection (EPSG:32643), frontage & side buffers | ✅ Complete |
| **Batch 6** | Phase 3 FAR & Coverage Audit | Table 6 Rule 50 compliance, built-up area validation | ✅ Complete |
| **Batch 7** | LLM Explainer Agent | Cognitive orchestrator (`agent.py`) with Gemini/OpenAI failover | ✅ Complete |
| **Batch 8** | Interactive GIS Dashboard | React 18 + Vite + Leaflet mapping and report drawer | ✅ Complete |
| **Batch 9** | Multi-Hazard & Benchmark Suite | Horn’s slope calculation, DEM classification, 69-test suite | ✅ Complete |

---

### Phase 2: Advanced Simulations & Multi-Modal Intelligence (Batches 10 – 18) — **🚧 Planned & In Progress**
* These subsequent modules extend the platform into advanced physics simulations, remote sensing, and cryptographic records.

| Batch | Planned Module | Technical Objective | Status |
| :--- | :--- | :--- | :---: |
| **Batches 10–12** | Hydrodynamic 2D Simulation | Physics-based flow-routing and runoff flash-flood modeling | 🚧 In Progress |
| **Batches 13–15** | Satellite & SAR Change Detection | Multi-temporal Sentinel-1 SAR & optical change detection deltas | 📅 Planned |
| **Batches 16–17** | Safe Corridor Routing | Dynamic flood evacuation pathfinding ($A^*$ / Dijkstra) | 📅 Planned |
| **Batch 18** | Cryptographic Audit Ledger | SHA-256 tamper-proof municipal record-keeping & audit trails | 📅 Planned |

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    User["Municipal Officer / Planner / Citizen"] --> Frontend["React.js + Leaflet Geospatial UI"]
    Frontend --> API["FastAPI Gateway (/api/v1)"]
    
    subgraph Core Engines [Core Computational Engines]
        API --> Phase1["Phase 1: Zoning & Statutory Land Classification"]
        API --> Phase2["Phase 2: Cadastral Topology & Setback Buffers"]
        API --> Phase3["Phase 3: Multi-Hazard, Slope & FAR / Coverage Audit"]
        API --> Agent["Agentic Explainer & Statutory RAG Copilot"]
    end
    
    subgraph Data Tier [Data & Storage Tier]
        Phase1 & Phase2 & Phase3 --> PostGIS[("PostgreSQL 16 + PostGIS\n(R-Tree Spatial Index)")]
        Agent --> PGVector[("pgvector Embeddings\n(HNSW Vector Index)")]
    end
```

---

## ✨ Implemented Core Capabilities

1. **Phase 1: Statutory Zoning & Due Diligence**
   - Automated screening against the **Kerala Conservation of Paddy Land and Wetland Act, 2008**.
   - Identifies restricted nilam/paddy zones, water body buffer prohibitions, and coastal CRZ/floodplain risks.

2. **Phase 2: Cadastral Boundaries & Precise Metric Setbacks**
   - Metric planar buffering (`ST_Transform` to EPSG:3857 / EPSG:32643) for exact frontage, rear, and side yard setbacks under **KMBR 2019** (Rules 23, 25, 27) and **KPBR 2019**.
   - Computes compliant buildable footprints from parcel geometries.

3. **Phase 3: Multi-Hazard Analysis & FAR Compliance**
   - Horn’s slope calculation and Digital Elevation Model (DEM) risk stratification.
   - Floor Area Ratio (FAR), Maximum Coverage %, and parking / access width verification against Table 6 (Rule 50).

4. **Agentic Explainer & Statutory RAG**
   - Cognitive orchestrator that translates spatial computation outputs into plain-language statutory explanations.
   - Dynamic multi-provider failover: automatic fallback across Google Gemini, OpenAI, local Ollama, or deterministic fallback engines.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, GeoAlchemy2, Pydantic v2
- **Spatial Database:** PostgreSQL 16, PostGIS 3.4 (R-Tree), pgvector 0.7+ (HNSW)
- **Geospatial Processing:** GDAL/OGR, Shapely, OSMnx, PyProj, NumPy
- **AI & RAG:** Google Gemini API, OpenAI API, LangChain / pgvector cosine similarity search
- **Frontend:** React 18, Vite, Leaflet, React-Leaflet, TailwindCSS
- **Containerization & CI:** Docker Compose, PyTest (69 automated unit & regression tests)

---

## 🚀 Quick Start Guide

### 1. Clone Repository & Setup Environment
```bash
git clone https://github.com/NaveenSuresh07/georag-plus.git
cd georag-plus
cp .env.example .env
```

### 2. Database Setup (Docker)
```bash
docker-compose up -d

# Verify database health
docker exec -it georag-db pg_isready -U georag
```

### 3. Backend Setup
```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt

# Run migrations & seed rule parameters
python scripts/load_rule_params.py

# Run test suite (69 tests)
pytest tests/ -v

# Start FastAPI dev server
uvicorn app.main:app --reload --port 8000
```
Backend API interactive docs: `http://localhost:8000/docs`.

### 4. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
Interactive GIS Dashboard: `http://localhost:5173`.

---

## 🧪 Testing & Verification

The core engine is backed by an automated verification suite covering edge cases, irregular parcels, and statutory corner cases:

```bash
cd backend
pytest tests/ -v
```
- ✅ **Test Coverage:** 69 passing test cases
- ✅ **Statutory Benchmarks:** 20 ground-truth cadastral plots in Attingal Municipality verified against official master plan records.

---

## 📄 License & Academic Attribution
Developed as part of the **GeoRAG+ Research Initiative (Group - 6)**.  
Open-source under the [MIT License](LICENSE).
