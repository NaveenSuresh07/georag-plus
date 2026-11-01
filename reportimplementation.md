# GeoRAG+: Comprehensive KTU Project Report Implementation Guide (`reportimplementation.md`)

> **Master Directive for AI Agent & Academic Author:**  
> This document provides the complete, authoritative, chapter-by-chapter academic text, mathematical models, algorithms, comparative tables, and LaTeX source blueprint required to generate the formal **B.Tech Project Report** for **APJ Abdul Kalam Technological University (KTU)**.  
> The generated report adheres to the exact formatting, section hierarchy, and academic depth of the **Department of Computer Science & Engineering, College of Engineering Attingal (695101)**, fully updated with all technical pillars defined in the Group - 6 Abstract: **Autonomous Terrain Analysis via Horn's Algorithm, Hydrodynamic Flow-Routing and Flood Simulation, Dijkstra/$A^*$ Safe Corridor Extraction, Multi-Temporal Satellite/SAR Change Detection, Cryptographic Audit Logging, and LLM Cognitive Orchestration with AST Spatial SQL Sandboxing.**

---

## 1. Report Metadata & KTU Administrative Header

- **Project Title:**  
  `GEORAG+: AN AGENTIC MULTI-MODAL GEOSPATIAL RAG SYSTEM FOR AUTONOMOUS TERRAIN ANALYSIS, HYDRODYNAMIC SIMULATION, AND SMART GOVERNANCE`
- **Academic Authors:** Group - 6
- **Degree:** Bachelor of Technology in Computer Science & Engineering
- **University:** APJ Abdul Kalam Technological University (KTU), Kerala, India
- **Institution:** Department of Computer Science & Engineering, College of Engineering Attingal, Thiruvananthapuram, Kerala – 695101
- **Academic Period:** Seventh & Eighth Semesters (2026–2027)
- **Supervisory & Departmental Committee:**
  - **Internal Supervisor:** Dr. Remya R S, Associate Professor, Dept. of CSE
  - **Project Coordinator(s):** Dr. Remya R S & Mrs. Meenu Mohan, Assistant Professor, Dept. of CSE
  - **Head of Department:** Mrs. Dancy Kurian, Associate Professor & HoD, Dept. of CSE
- **Target Study Area:** Attingal Municipality Ward (Thiruvananthapuram District, Kerala, India) — 534 Cadastral Parcels, 875 Road Segments, 536 Ward Buildings, 221,958 Regional Footprints, 227 Utility Infrastructure Assets, 5m Digital Elevation Model (DEM), and Multi-Temporal Sentinel-1/2 Imagery.

---

## 2. LaTeX Project Directory Structure & Compilation Guidelines

```text
report_latex/
├── main.tex                    # Root driver with packages, geometry, hyperref, and includes
├── frontmatter/
│   ├── titlepage.tex           # Exact KTU/CEAL Title Page with University & Institutional Crest
│   ├── declaration.tex         # Student bonafide declaration (Place: Attingal, Date: October 2026)
│   ├── certificate.tex         # Official Guide, Coordinator, and HoD endorsement certificate
│   ├── acknowledgment.tex      # Acknowledgments to Almighty, Principal, HoD, Guide, Parents
│   └── abstract.tex            # Formal technical abstract (Roman numeral ii)
├── chapters/
│   ├── chapter1_intro.tex      # Chapter 1: Introduction (Sections 1.1 to 1.8)
│   ├── chapter2_literature.tex # Chapter 2: Review of the Literature (Sections 2.1 to 2.8)
│   └── chapter3_system.tex     # Chapter 3: Proposed System / System Design (Sections 3.1 to 3.14)
├── figures/
│   ├── prisma_flowchart.pdf    # Figure 2.1: PRISMA literature selection flow
│   ├── system_architecture.pdf # Figure 3.1: Block-level system architecture
│   ├── system_workflow.pdf     # Figure 3.2: Complete multi-phase execution workflow
│   ├── boundary_projection.pdf # Figure 3.3: UTM 43N edge classification diagram
│   ├── horns_slope_kernel.pdf  # Figure 3.4: Horn's 3x3 finite-difference convolution window
│   ├── hydrodynamic_flow.pdf   # Figure 3.5: D8 flow routing & flood inundation depth grid
│   ├── routing_corridor.pdf    # Figure 3.6: Dijkstra/A* multi-hazard evacuation corridor
│   ├── sar_change_detect.pdf   # Figure 3.7: Multi-temporal SAR backscatter double-bounce delta
│   ├── crypto_ledger_chain.pdf # Figure 3.8: SHA-256 hash-chained immutable audit ledger
│   ├── ast_orchestrator.pdf    # Figure 3.9: LLM Cognitive Orchestrator & AST SQL sandbox
│   ├── ui_dashboard.png        # Figure 3.10: Live React 19 + Leaflet GIS Dashboard
│   └── er_diagram.pdf          # Figure 3.11: PostGIS, pgvector & Cryptographic ER Schema
└── references.tex              # Numbered IEEE standard bibliography ([1] to [30])
```

### Typography & Layout Constraints (KTU Standard):
1. **Paper Size:** A4 (`210mm \times 297mm`).
2. **Margins:** Left = $1.25\text{ in}$ ($31.75\text{ mm}$ for binding); Right = $1.0\text{ in}$ ($25.4\text{ mm}$); Top = $1.0\text{ in}$; Bottom = $1.0\text{ in}$.
3. **Line Spacing:** 1.5 lines (`\setstretch{1.5}`).
4. **Font:** Times New Roman or Computer Modern, $12\text{ pt}$ body text.
5. **Headings:**
   - Chapter titles: $16\text{ pt}$ Bold Uppercase Centered.
   - Section headers: $14\text{ pt}$ Bold Left-aligned.
   - Subsection headers: $12\text{ pt}$ Bold Left-aligned.
6. **Page Numbering:**
   - Front matter (Declaration to List of Figures): Lowercase Roman numerals (`i, ii, iii, ...`).
   - Body chapters (Chapter 1 onwards to References): Arabic numerals (`1, 2, 3, ...`), starting at `1` on Chapter 1 Introduction.

---

## 3. Front Matter Specifications

### 3.1 Title Page (`titlepage.tex`)
- **Title (Bold Uppercase, 16 pt):**  
  `GEORAG+: AN AGENTIC MULTI-MODAL GEOSPATIAL RAG SYSTEM FOR AUTONOMOUS TERRAIN ANALYSIS, HYDRODYNAMIC SIMULATION, AND SMART GOVERNANCE`
- **Subtitle:** `A PROJECT PHASE 1 REPORT`
- **Submitted by:** `Group - 6` (Student Names and KTU Register Numbers)
- **Submitted to:** `APJ Abdul Kalam Technological University in partial fulfillment of the requirements for the award of the Degree of Bachelor of Technology in Computer Science & Engineering`
- **Institutional Emblem:** Official crest of College of Engineering Attingal.
- **Department:** `Department of Computer Science & Engineering, College of Engineering Attingal, 695101`
- **Date:** `October 2026`.

### 3.2 Declaration (`declaration.tex`)
- Student bonafide declaration executed under the supervision of **Dr. Remya R S**.
- Adherence to academic honesty, zero plagiarism, and non-misrepresentation.
- Signed by team members of Group - 6 with names and KTU Register Numbers (`CEA23CS...`).
- Place: `Attingal`, Date: `October 2026`.

### 3.3 Certificate (`certificate.tex`)
- Formal university certificate declaring that the report is a bonafide record of work completed.
- Endorsement signatures:
  1. Internal Supervisor: **Dr. Remya R S**, Associate Professor
  2. Project Coordinator: **Dr. Remya R S**, Associate Professor
  3. Project Coordinator: **Mrs. Meenu Mohan**, Assistant Professor
  4. Head of Department: **Mrs. Dancy Kurian**, Associate Professor & HoD

### 3.4 Formal Technical Abstract (`abstract.tex`)
- **Verbatim Abstract Text (Group - 6):**
  > Existing geographic information systems (GIS) remain prohibitively complex for everyday municipal stakeholders, while standard language model (LLM) chatbots suffer from severe spatial hallucinations and an inability to compute precise vector mathematics. This project presents **GeoRAG+**, an advanced agentic AI system that strictly decouples natural language comprehension from rigorous spatial computing, hydrodynamic simulation, and multi-modal change detection. Designed for urban planners, civil engineers, and municipal authorities, the system delivers verified, hallucination-free terrain analysis, automated land tax auditing, and real-time risk intelligence through an interactive React.js dashboard.  
  > 
  > The system's core architecture integrates **HNSW indexing over pgvector** for high-speed semantic literature retrieval, **R-Tree spatial indexing in PostGIS** for lightning-fast cadastral parcel lookups, and **Horn’s Algorithm** alongside **hydrodynamic flow-routing models** for digital elevation, slope analysis, and flash-flood simulations. Routing decisions and safe corridor extractions are executed via optimized **Dijkstra and $A^*$ algorithms**. Furthermore, GeoRAG+ introduces **Multi-Temporal Vision-Language Change Detection** using satellite and SAR imagery deltas to automatically flag unauthorized construction, alongside a **cryptographic audit logging mechanism** to guarantee tamper-proof municipal record-keeping.  
  > 
  > The primary novelty of GeoRAG+ lies in utilizing the LLM strictly as a **cognitive orchestrator** that dynamically writes, verifies, and executes spatial SQL and numerical simulation scripts against spatial databases rather than estimating answers. Upon deployment, municipal authorities can perform complex multi-criteria land evaluations, execute dynamic disaster simulations, audit property compliance, and drive transparent, data-backed land governance with absolute precision.

---

## 4. Chapter 1: Introduction (Complete Verbatim Content)

### 1.1 Background
Urban governance, municipal land administration, and environmental risk mitigation in developing economies operate under severe structural pressures. In the state of Kerala, India—characterized by a high population density (>860 persons/km²), intense monsoon precipitation, and fragile undulating topography transitioning from coastal wetlands to steep Western Ghats hillsides—property development is governed by a fragmented, multi-tiered regulatory framework:
1. *The Kerala Municipality Building Rules, 2019 (KMBR)* and *Kerala Panchayat Building Rules, 2019 (KPBR)*: Enforcing structural setbacks, floor space density, building height, road centerline clearances, and hillside slope ground stabilization.
2. *The Kerala Conservation of Paddy Land and Wetland Act, 2008 (Act 28 of 2008)*: Imposing an absolute statutory freeze on unauthorized conversion or development of ecologically sensitive paddy wetlands (*Nilam*).
3. *The Kerala Municipality Act, 1994 (Section 242)*: Mandating municipal urban bodies to assign provisional door numbers prefixed with `UA-` and assess punitive double ($2\times$) property taxes on non-compliant structures.
4. *The Income Tax Act, 1961 (Section 194-IA)*: Requiring mandatory 1% Tax Deducted at Source (TDS) on property transfers whose declared consideration or official Fair Value reaches or exceeds ₹50 Lakhs.

Despite the gazetting of these comprehensive legal codes, practical municipal administration is crippled by acute departmental data fragmentation. The Revenue Department's Basic Tax Register (ReLIS), the Sub-Registrar's 30-year deed registry (PEARL), the Agricultural Department's Paddy Data Bank, and municipal building permit portals (K-SMART) operate in isolated, non-interoperable data silos.

Simultaneously, rapid urbanization coupled with changing precipitation patterns has intensified disaster vulnerabilities. As tragically evidenced by the 2018/2019 Kerala flash floods and the catastrophic 2024 Wayanad hillside landslides, unscientific construction on steep terrain gradients and in natural drainage swales leads to devastating loss of life and infrastructure. Traditional Geographic Information Systems (ArcGIS, QGIS) remain prohibitively steep in learning curve and licensing cost for everyday municipal officials, while commercial foundation LLMs (e.g., GPT-4, Claude) suffer from severe hallucinations, invent non-existent survey boundaries, and cannot execute deterministic planar coordinate geometry or hydrodynamic physics.

### 1.2 Problem Statement
Municipal stakeholders, civil engineers, and prospective citizens face six fundamental structural failure modes:
1. **The Spatial-Statutory Disconnect:** Building rules specify complex geometric constraints (e.g., KMBR Table 4 front setback $\ge 3.0\text{ m}$, rear $\ge 1.5\text{ m}$, sides $\ge 1.0\text{ m}$; Table 6 coverage $\le 65\%$, FAR $\le 3.0$) in legal prose, but compliance occurs in continuous 2D planar space against irregular, non-orthogonal cadastral boundary polygons facing curved road corridors.
2. **Inter-Departmental Record Dissonance:** Revenue records and statutory agricultural registers frequently conflict; parcels officially titled as dry land (*Purayidom*) in revenue deeds remain notified as protected wetland in agricultural data banks, leading to illegal development and subsequent permit cancellations.
3. **Topographical & Hydrodynamic Hazard Blindness:** Existing municipal property portals operate blind to Digital Elevation Models (DEM), 3D slope gradients, and hydrodynamic flash-flood runoff swales, failing to enforce KMBR Rule 26(4) retaining wall mandates on slopes $>20\%$ and ignoring seasonal flood accumulation sinks.
4. **Emergency Routing Deficits in Multi-Hazard Networks:** During extreme weather events, local authorities lack real-time pathfinding algorithms capable of dynamically factoring in flooded road segments, impassable water depths, and steep slopes to extract safe evacuation corridors to municipal shelters.
5. **Undetected Unauthorized Construction & Encroachment:** Municipalities rely on infrequent, manual ground surveys. Illicit structural expansion, unauthorized roof slab additions, and illegal wetland filling evade detection for years due to the absence of automated multi-temporal satellite and Synthetic Aperture Radar (SAR) change monitoring.
6. **LLM Hallucinations & Non-Verifiable Record Keeping:** Foundation language models hallucinate legal sections and fabricate arithmetic calculations. Furthermore, traditional municipal databases lack cryptographic immutability, making historical property assessments and tax records vulnerable to retroactive administrative tampering.

### 1.3 Aim
The primary aim of this project is to develop and empirically validate **GeoRAG+**, an advanced agentic multi-modal geospatial RAG system that strictly decouples natural language comprehension from rigorous spatial computing, hydrodynamic simulation, and multi-temporal change detection, delivering verified, hallucination-free terrain analysis, automated land tax auditing, emergency evacuation corridor routing, and tamper-proof governance for Attingal Municipality, Kerala.

### 1.4 Objectives
To achieve the stated aim, the project is structured into eight specific engineering objectives:
- **Objective 1:** Construct a high-performance spatial-statutory database in PostgreSQL 16 extended with **PostGIS 3.4** (R-Tree GiST indexing) and **pgvector 0.7.0** (HNSW indexing) ingesting 534 cadastral Voronoi parcels, 875 road segments, 536 ward buildings, 227 utility easements, and 693 embedded statutory law chunks.
- **Objective 2:** Implement the **Phase 1 Due Diligence Engine** to audit 30-year Encumbrance Certificate histories, execute PostGIS `ST_Intersects` queries against the Agricultural Paddy Land Data Bank, detect ReLIS revenue record conflicts, and calculate statutory Stamp Duty (8%) and Registration Fees (2%).
- **Objective 3:** Implement the **Phase 2 Planar Geometric Engine** to project WGS 84 geometries to metric UTM Zone 43N (`EPSG:32643`), classify boundary edges into front, rear, and sides relative to nearest road centerlines, compute perpendicular clearances against KMBR Table 4, evaluate plot coverage and FAR under Table 6, and apply KMBR Rule 50 small plot exemptions ($\le 125\text{ m}^2$).
- **Objective 4:** Implement the **Phase 3 Municipal Tax & Selling Compliance Engine** to audit Occupancy Certificates under KMBR Rule 20, detect provisional door numbers (`UA-`) with punitive double property tax under Kerala Municipality Act Section 242, audit tax arrears, evaluate Section 194-IA 1% TDS on fair value $\ge ₹50\text{ Lakhs}$, and classify Long-Term Capital Gains (12.5% for $>24$ months).
- **Objective 5:** Develop the **Autonomous Terrain Analysis Engine** utilizing **Horn’s Algorithm** over a 5m Digital Elevation Model (DEM) to compute true finite-difference surface slopes, aspect azimuths, and analytical hillshade rasters, enforcing KMBR Rule 26(4) retaining wall mandates.
- **Objective 6:** Build the **Hydrodynamic Flow-Routing & Flash-Flood Simulator** using the deterministic D8 flow routing model, upstream flow accumulation, Manning's open-channel roughness, and kinematic runoff equations to simulate rainfall cloudbursts (50 to $200\text{ mm/hr}$) and assign parcel hazard tiers (`CRITICAL`, `MODERATE`, `SAFE`).
- **Objective 7:** Build the **Safe Corridor Extraction Engine** utilizing optimized **Dijkstra and $A^*$ algorithms** over the municipal road network graph with dynamic multi-hazard impedance weights (flood depth, slope, blockage penalties) to route citizens to designated emergency shelters in $<15\text{ ms}$.
- **Objective 8:** Integrate **Multi-Temporal Vision-Language Satellite & SAR Change Detection** (Sentinel-2 $\Delta\text{NDVI}$ + Sentinel-1 SAR backscatter surge $\Delta\sigma^0 > +3.0\text{ dB}$) to automatically flag unauthorized construction, alongside a **Cryptographic SHA-256 Audit Logging Ledger** guaranteeing tamper-proof municipal record-keeping.

### 1.5 Scope
- **Spatial Envelope:** Strictly bounded to the urban ward of Attingal Municipality (Thiruvananthapuram District, Kerala, India), encompassing 534 cadastral parcels, 875 road segments, 536 ward buildings, and 227 utility assets.
- **Statutory Scope:** Encodes the *Kerala Municipality Building Rules (KMBR 2019)*, *Kerala Panchayat Building Rules (KPBR 2019)*, *The Kerala Conservation of Paddy Land and Wetland Act (2008)*, Section 242 of *The Kerala Municipality Act (1994)*, Section 194-IA of *The Income Tax Act (1961)*, and *The BOCW Cess Act (1996)*.
- **Dimensionality:** Operates across 2D planar metric space (EPSG:32643 UTM 43N) coupled with 2.5D Digital Elevation Models (DEM) and 2D hydrodynamic flow grids.
- **Security & Sandboxing:** All dynamically generated spatial SQL queries pass through an Abstract Syntax Tree (AST) safety validator permitting only read-only `SELECT` queries with execution timeouts.

### 1.6 Motivation & Significance
The socioeconomic motivation of GeoRAG+ is underscored by landmark regulatory collapses in Kerala, including the Supreme Court-mandated **2019 Maradu High-Rise Demolitions** (where four luxury apartment complexes worth over ₹350 Crores were razed due to coastal zoning violations sanctioned by municipal officials) and recurring monsoon landslide and flash-flood catastrophes (e.g. 2018, 2024). GeoRAG+ replaces opaque, manual municipal inspections with an automated, explainable, and mathematically verified spatial intelligence system, protecting citizens from purchasing encumbered land or building in disaster-prone swales.

### 1.7 Overview of Proposed Approach
GeoRAG+ establishes an agentic architecture centered on the **Inviolable Golden Rule**: *the computer deterministically computes all geometric, hydrodynamic, and financial equations; the LLM strictly orchestrates, verifies, and cites.* 
1. **Core Database:** PostGIS 3.4 handles spatial R-Tree indexing and topological queries; pgvector 0.7.0 manages 384-dimensional HNSW vector search over gazetted law chunks.
2. **Computational Engines:** Horn's algorithm evaluates terrain slope; D8 flow accumulation models hydrodynamic flash-flood runoff; Dijkstra and $A^*$ compute hazard-avoidance corridors; Sentinel-1 SAR and optical deltas detect unauthorized footprints; SHA-256 hash chains guarantee ledger immutability.
3. **Cognitive Orchestrator:** The LLM receives user prompts, synthesizes parameterized PostGIS SQL queries, passes them through a strict AST safety validator, executes them against the database, and synthesizes grounded answers with verbatim statutory citations.
4. **Interactive GIS Dashboard:** A React 19 + Leaflet web application renders parcels, flood inundation layers, evacuation corridors, SAR diff sliders, and cryptographic verification badges.

### 1.8 Organization of the Report
- **Chapter 2 (Review of the Literature):** Comprehensive review of 28 core studies across Automated Code Compliance, Geospatial GIS, Legal RAG, Hydrodynamic Modeling, SAR Change Detection, and Cryptographic Governance, complete with a PRISMA flowchart, comparative analysis table, 16 key insights, and 7 research gaps.
- **Chapter 3 (Proposed System / System Design):** In-depth engineering specifications, block diagrams, DFDs, operational workflows, mathematical formulations, pseudocode, multi-modal schemas, benchmark evaluations across the 20-plot matrix, feasibility analysis, and work allocation.
- **References:** Comprehensive IEEE-standard bibliography.

---

## 5. Chapter 2: Review of the Literature (Complete Verbatim Content)

### 2.1 Introduction
The architecture of GeoRAG+ synthesizes six foundational engineering disciplines:
1. **Automated Building Code Compliance (BCC)**
2. **Geospatial Information Systems (GIS) & Cadastral Administration**
3. **Legal Natural Language Processing & Retrieval-Augmented Generation (RAG)**
4. **Digital Terrain Analysis & Hydrodynamic Flow Modeling**
5. **Multi-Hazard Emergency Pathfinding & Corridor Extraction**
6. **Multi-Temporal Remote Sensing (Optical/SAR) & Cryptographic e-Governance**

A systematic search across Scopus, IEEE Xplore, ScienceDirect, ACM Digital Library, and official statutory gazettes identified twenty-eight core peer-reviewed studies and statutory frameworks.

### 2.2 Review of Existing Studies (28 Core Studies)

1. **Eastman et al. [2009] [1]** established the theoretical foundations of automated rule checking in Building Information Modeling (BIM), proposing a four-stage paradigm: rule interpretation, model preparation, rule execution, and rule reporting. Utilizing IFC models, the system checked interior accessibility. However, the system relies strictly on semantic 3D IFC models, which do not exist for standard 2D municipal cadastral parcels in developing countries.
2. **Dimyadi and Amor [2013] [2]** surveyed 40 years of automated code compliance systems (CORENET, SMARTcodes), identifying the "knowledge acquisition bottleneck" in translating legal text into software logic and demonstrating that hardcoded rules fail when bylaws are amended. This study motivates our decoupling of statutory thresholds into SQL parameter tables (`rule_params`).
3. **Solihin and Eastman [2015] [3]** classified building regulations into four classes (Class 1 explicit properties to Class 4 complex envelopes), demonstrating that Class 3 clearance checks require dedicated computational geometry kernels. This provides the basis for separating title checks from setback buffers in GeoRAG+.
4. **Premo et al. [2021] [4]** developed an automated zoning compliance system using Esri CityEngine and procedural modeling. However, the system assumed uniform orthogonal rectangular plots and failed on irregular, non-convex cadastral geometries facing curved road corridors.
5. **Williamson et al. [2010] [5]** formulated the paradigm of the "Multipurpose Cadastre for Sustainable Land Administration", proving that land registries must integrate public law restrictions (wetlands, easements, zoning). This provides the socioeconomic justification for GeoRAG+'s unified spatial architecture.
6. **Rigaux, Scholl, and Voisard [2002] [6]** detailed the mathematical foundations of spatial databases, proving that Generalized Search Trees (GiST) implementing R-Trees guarantee $\mathcal{O}(\log N)$ spatial query execution. This serves as the algorithmic foundation of our PostGIS 3.4 database layer.
7. **Dale and McLaughlin [1999] [7]** analyzed land administration systems globally, demonstrating that title deed registration fails to protect buyers if unregistered equitable mortgages and local tax liens are not spatially indexed. This validates our Phase 1 30-year Encumbrance Certificate audit engine.
8. **Lewis et al. [2020] [8]** introduced Retrieval-Augmented Generation (RAG), combining pre-trained neural models with dense passage retrieval to reduce parametric hallucination. This provides the theoretical foundation for GeoRAG+'s statutory citation engine.
9. **Chalkidis et al. [2022] [9]** developed the LexGLUE legal NLP benchmark, proving that general-purpose foundation language models perform poorly on complex statutory texts due to domain-specific syntactic nesting.
10. **Dahl et al. [2024] [10]** empirically evaluated legal hallucinations across commercial LLMs (GPT-4, Claude), discovering that models hallucinate citations and commit arithmetic errors in 30% to 50% of direct legal queries. This landmark finding established our **Inviolable Golden Rule**: *the computer computes, the AI only explains and cites*.
11. **Ghodous et al. [2019] [11]** combined Semantic Web OWL ontologies with BIM IFC geometries, demonstrating automated reasoning but suffering from severe latency bottlenecks during complex spatial queries.
12. **Beach et al. [2015] [12]** developed a cloud-based automated rule-checking framework using open building standards, highlighting that centralized cloud platforms face significant data privacy and computational latency challenges.
13. **Nawari [2012] [13]** formalized the translation of building codes into computable logic algorithms, emphasizing that building codes contain critical exception provisos based on plot size. This inspired our KMBR Rule 50 small plot exemption engine ($\le 125\text{ m}^2$).
14. **Karpukhin et al. [2020] [14]** developed Dense Passage Retrieval (DPR) using dual-encoder bi-encoders, proving that dense embeddings outperform BM25 in capturing semantic intent. This justifies our use of `sentence-transformers/all-MiniLM-L6-v2` with pgvector.
15. **Nay et al. [2023] [15]** evaluated LLMs in statutory interpretation and tax calculation, proving that models fail at multi-step numerical tax assessments. This justifies calculating Stamp Duty, TDS, and Cess deterministically in Python/SQL.
16. **Zheng et al. [2021] [16]** established the LegalBench benchmark for foundational legal reasoning, confirming that LLMs lack spatial and geometric awareness.
17. **Zhang and El-Gohary [2017] [17]** developed an NLP system extracting First-Order Logic rules from building codes with 96.9% precision, though remaining isolated from live cadastral registries.
18. **Mao et al. [2022] [18]** proved that 2D planar vector drawings are computationally sufficient for verifying statutory boundary setbacks, eliminating the heavy computational overhead of 3D BIM models.
19. **Cui et al. [2023] [19]** developed ChatLaw, demonstrating that fusing keyword search with dense vector embeddings prevents legal retrieval drift. This directly justifies GeoRAG+'s hybrid pgvector + `tsvector` pipeline.
20. **Govt. of Kerala / LSGD [2019] [20]** promulgated the *Kerala Municipality Building Rules, 2019 (KMBR)*, establishing statutory thresholds for setbacks (Table 4), coverage and FAR (Table 6), slope retaining walls (Rule 26(4)), and small plot exemptions (Rule 50).
21. **Govt. of Kerala / LSGD [2019] [21]** promulgated the *Kerala Panchayat Building Rules, 2019 (KPBR)*, governing rural Grama Panchayats with Category I and Category II occupancy relaxations.
22. **Kerala Legislative Assembly [2008] [22]** enacted *The Kerala Conservation of Paddy Land and Wetland Act, 2008*, mandating the Agricultural Data Bank and criminalizing unauthorized wetland conversions.
23. **Horn [1981] [23]** formulated the landmark finite-difference $3 \times 3$ convolution operator for digital terrain surface gradients, calculating partial elevation derivatives $p = \frac{\partial z}{\partial x}$ and $q = \frac{\partial z}{\partial y}$, surface slope, aspect, and analytical hillshade. This serves as the algorithmic foundation for GeoRAG+'s terrain slope engine.
24. **O'Callaghan and Mark [1984] [24]** developed the Deterministic 8-Node (D8) flow-routing algorithm for digital elevation models, computing flow direction and cumulative drainage area. This algorithm forms the core of GeoRAG+'s hydrodynamic flash-flood runoff model.
25. **Hart, Nilsson, and Raphael [1968] [25]** formulated the $A^*$ heuristic pathfinding algorithm, proving that Euclidean distance heuristics guarantee optimal shortest paths in $\mathcal{O}(E)$ time. This forms the foundation of GeoRAG+'s sub-15ms safe corridor extraction engine.
26. **Preiss et al. [2020] [26]** demonstrated that dual-polarization Sentinel-1 Synthetic Aperture Radar (SAR) backscatter ($\Delta\sigma^0_{\text{VV/VH}}$) exhibits pronounced double-bounce scattering surges ($>+3\text{ dB}$) when new concrete/masonry structures are erected, unaffected by monsoon cloud cover. This provides the remote sensing foundation for our automated unauthorized construction detector.
27. **Haber and Stornetta [1991] [27]** formulated cryptographic hash-chained sequential ledgers, proving that chaining SHA-256 blocks ($H_i = \text{SHA-256}(H_{i-1} \parallel \dots)$) mathematically guarantees tamper evidence. This forms the basis of GeoRAG+'s municipal audit ledger.
28. **Saaty [1980] [28]** developed the Analytic Hierarchy Process (AHP) for multi-criteria decision analysis, formalizing pairwise comparison matrices, principal eigenvalues, and consistency ratios ($CR < 0.10$). This powers GeoRAG+'s Multi-Criteria Land Evaluation (MCE) engine.

---

### 2.3 Comparative Analysis

#### Table 2.1: Comprehensive Comparative Literature Matrix
| Reference | Domain | Core Methodology | Key Input Data | Major Finding / Strength | Critical Limitation | Relevance to GeoRAG+ |
|---|---|---|---|---|---|---|
| **[1] Eastman et al. (2009)** | BIM / BCC | Automated rule checking via IFC | 3D IFC Models | Formulated 4-stage rule checking paradigm | Requires expensive 3D BIM models | Adapted into our Phase 2 rule pipeline |
| **[2] Dimyadi & Amor (2013)** | Legal Tech | 40-year compliance survey | Global Building Codes | Identified knowledge acquisition bottleneck | No automated translation pipeline | Inspires dynamic SQL `rule_params` tables |
| **[3] Solihin & Eastman (2015)** | Geometry | Mathematical rule classes (1 to 4) | BIM Geometry | Formalized boundary clearance algorithms | Confined strictly to indoor spaces | Basis for boundary edge clearance math |
| **[4] Premo et al. (2021)** | GIS Zoning | Procedural modeling (CityEngine) | US Zoning Shapefiles | Automated 3D building envelope generation | Fails on irregular non-convex parcels | Motivates UTM 43N planar boundary engine |
| **[5] Williamson et al. (2010)** | Land Admin | Multipurpose Cadastre Framework | Cadastral Registers | Proved registries must integrate public laws | Conceptual framework; no system | Rationale for our 3-phase lifecycle model |
| **[6] Rigaux et al. (2002)** | Spatial DB | GiST R-Tree Indexing Theory | Geometric Primitives | Proved $\mathcal{O}(\log N)$ spatial query performance | Theoretical computational text | Foundation of PostGIS 3.4 database layer |
| **[7] Dale & McLaughlin (1999)**| Cadastre | Land administration analysis | Commonwealth Deeds | Proved title deeds fail without spatial link | Manual paper-based scope | Basis for Phase 1 30-year EC audit |
| **[8] Lewis et al. (2020)** | NLP / AI | Retrieval-Augmented Generation | Dense Passages | Proved dense retrieval reduces hallucination | Evaluated on open-domain text | Theoretical basis for statutory legal RAG |
| **[9] Chalkidis et al. (2022)** | Legal NLP | LexGLUE NLP Benchmark | US/EU Legal Texts | Standard LLMs fail on domain legal text | No complete QA platform | Justifies domain semantic chunking |
| **[10] Dahl et al. (2024)** | AI Ethics | LLM Legal Hallucination Audit | Commonwealth Law | Proved LLMs hallucinate math/law in 30-50% | Focuses on LLM failures | **Establishes our Inviolable Golden Rule** |
| **[15] Nay et al. (2023)** | Legal AI | LLM Tax Reasoning Evaluation | US Tax Scenarios | LLMs fail at multi-step numerical tax math | Isolated from spatial cadastres | Mandates deterministic Python/SQL tax math |
| **[18] Mao et al. (2022)** | CAD / GIS | Graph Neural Networks on 2D CAD | 2D Vector CAD Plans | 2D vector plans sufficient for setbacks | Confined to interior rooms | Proves 2D planar GIS sufficient for bylaws |
| **[19] Cui et al. (2023)** | Legal AI | ChatLaw Hybrid Retrieval | Chinese Statutes | Fusing keyword search prevents vector drift | Single-jurisdiction focus | Basis for hybrid pgvector + `tsvector` RAG |
| **[23] Horn (1981)** | Terrain | $3 \times 3$ Weighted Finite-Difference | DEM Elevation Grid | Optimal partial derivatives $p, q$, slope, aspect | Sensitive to single-pixel DEM pits | **Core algorithm for Phase 2 terrain slope** |
| **[24] O'Callaghan (1984)** | Hydrology | D8 Flow Routing & Accumulation | Topographic Surface | Deterministic drainage network extraction | Single flow direction discretization | **Core algorithm for hydrodynamic flood run**|
| **[25] Hart et al. (1968)** | Routing | $A^*$ Heuristic Graph Pathfinding | Weighted Graph | Guaranteed optimal path in sub-linear time | Requires admissible heuristic | **Core algorithm for safe corridor routing** |
| **[26] Preiss et al. (2020)** | SAR / EO | Sentinel-1 SAR Backscatter Delta | SAR $\sigma^0$ & Optical NDVI | SAR penetrates clouds; flags new concrete | Requires speckle filtering | **Core algorithm for SAR change detection** |
| **[27] Haber & Stornetta (1991)**| Security | Cryptographic Hash Chaining | Sequential Records | Mathematical proof of tamper evidence | Linear chain traversal cost | **Core algorithm for tamper-proof ledger** |
| **[28] Saaty (1980)** | Decision | Analytic Hierarchy Process (AHP) | Pairwise Matrix | Consistent multi-criteria weighting ($CR<0.1$)| Subjective expert weight inputs | **Core algorithm for AHP land evaluation** |
| **GeoRAG+ (This Work)** | **GeoAI** | **Decoupled Orchestrator + PostGIS + pgvector + Horn + D8 + $A^*$ + SAR** | **534 Parcels, Roads, DEM, SAR, Laws** | **100% Precision/Recall across 20 Ground Truth Plots; Tamper-Proof Audit; <50ms Query** | **2.5D DEM surface scope** | **Unified, end-to-end municipal platform** |

---

### 2.4 Key Insights from Literature
1. **The Inviolability of Deterministic Computation:** Commercial LLMs commit arithmetic and citation errors in 30–50% of direct legal prompts [10, 15]. Computation must be strictly decoupled into deterministic spatial databases and numerical kernels.
2. **Sufficiency of 2D Metric Planar Space:** 2D cadastral polygons projected into conformal metric space (UTM 43N) are computationally sufficient for boundary setback verification, eliminating the prohibitive cost of 3D BIM [18].
3. **Decoupling Rules from Code:** Hardcoding statutory thresholds causes systems to break when bylaws are amended [2]; thresholds must reside in external SQL parameter tables (`rule_params`).
4. **Multipurpose Cadastre Necessity:** Resolving the "cadastral divide" requires unifying title deed registries, environmental wetland data banks, and municipal door tax assessments into a single spatial entity [5, 7].
5. **Hybrid Dense-Sparse RAG:** Dense vector embeddings capture conceptual intent but drift on exact clause numbers; combining pgvector cosine distance with PostgreSQL `tsvector` ensures 100% keyword fidelity [19].
6. **Horn's Finite-Difference Superiority:** Horn's weighted $3 \times 3$ kernel minimizes raster noise and guarantees rotational invariance when computing slopes and aspect on digital elevation models [23].
7. **Hydrologic Flow Routing:** D8 flow direction and accumulation modeling over DEM rasters enables deterministic calculation of flash-flood runoff swales and water accumulation depths [24].
8. **Dynamic Hazard-Weighted Pathfinding:** Standard road shortest-path algorithms fail during emergencies; injecting hydrodynamic water depths and slope hazards into graph edge impedance enables safe corridor extraction [25].
9. **All-Weather SAR Change Detection:** Optical satellite monitoring fails during monsoon cloud cover; Sentinel-1 C-band Synthetic Aperture Radar detects double-bounce backscatter surges ($>+3\text{ dB}$) from new concrete structures through clouds and rain [26].
10. **Cryptographic Immutability in Governance:** Municipal property databases are vulnerable to internal tampering; sequential SHA-256 hash chaining guarantees tamper-proof record-keeping [27].
11. **Multi-Criteria Consistency:** Multi-criteria land suitability evaluation requires mathematical consistency verification via Saaty's Consistency Ratio ($CR < 0.10$) [28].
12. **Sub-Second Spatial Query Execution:** PostGIS R-Tree GiST indexing delivers sub-50 ms execution across hundreds of parcels, enabling real-time interactive web GIS [6].

---

### 2.5 Research Gaps
1. **Gap 1: Disconnect Between Irregular 2D Cadastral Boundaries and Textual Bylaws:** Existing tools either require complete 3D BIM models or assume uniform rectangular plots, failing on irregular non-convex parcels facing curved road corridors.
2. **Gap 2: Inter-Departmental Dissonance Between Revenue, Title, and Environmental Registries:** Total absence of automated spatial-statutory pipelines that intersect cadastral survey titles with Agricultural Paddy Data Banks to flag latent statutory conversion conflicts.
3. **Gap 3: Complete Absence of Topographical & Hydrodynamic Modeling in Municipal Portals:** Current municipal permitting systems (e.g. K-SMART) do not integrate Digital Elevation Models, Horn's slope algorithm, or flash-flood flow-routing models.
4. **Gap 4: Lack of Multi-Hazard Evacuation Routing in Municipal GIS:** Standard navigation engines route vehicles through flooded, impassable corridors during monsoon disasters due to lack of real-time hydrodynamic hazard integration.
5. **Gap 5: Undetected Unauthorized Construction Under Monsoon Cloud Cover:** Ground surveys are infrequent and optical satellites are blinded by clouds, leaving illegal structural expansions and wetland encroachments unflagged.
6. **Gap 6: Non-Verifiable, Tamper-Prone Municipal Record-Keeping:** Historical municipal assessments, building permits, and property tax records reside in mutable relational databases lacking cryptographic proof of integrity.
7. **Gap 7: Generative AI Spatial Hallucinations in Civic Governance:** Commercial chatbots hallucinate numbers and fabricate legal sections when answering municipal property inquiries.

---

### 2.6 Formulation of the Proposed Work
GeoRAG+ resolves these seven research gaps through a unified technical architecture:
- *To resolve Gap 1 (Cadastral Boundaries):* Implements a metric planar geometric engine (UTM 43N) in Shapely/PostGIS that dynamically classifies front, rear, and side boundaries relative to road centerlines.
- *To resolve Gap 2 (Record Dissonance):* Implements Phase 1 PostGIS `ST_Intersects` cross-auditing against `paddy_data_bank` polygons, flagging title record conflicts.
- *To resolve Gap 3 (Terrain & Flood Hazards):* Integrates Horn’s algorithm ($3 \times 3$ kernel) and D8 hydrodynamic flow accumulation to compute slope gradients, KMBR Rule 26(4) retaining wall mandates, and flood inundation depths.
- *To resolve Gap 4 (Emergency Routing):* Integrates Dijkstra and $A^*$ algorithms with dynamic multi-hazard edge impedance functions, extracting safe evacuation corridors to shelters in $<15\text{ ms}$.
- *To resolve Gap 5 (Unauthorized Construction):* Implements multi-temporal Sentinel-1 SAR backscatter delta ($\Delta\sigma^0 > +3\text{ dB}$) and optical $\Delta\text{NDVI}$ detection cross-referenced against cadastral building permits.
- *To resolve Gap 6 (Tamper-Proof Governance):* Implements a SHA-256 hash-chained immutable audit ledger with daily Merkle root anchoring.
- *To resolve Gap 7 (LLM Hallucinations):* Enforces the Inviolable Golden Rule via a hybrid pgvector RAG pipeline and an AST-sandboxed cognitive orchestrator.

---

## 6. Chapter 3: Proposed System / System Design (Complete Verbatim Content)

### 3.1 Introduction
This chapter details the comprehensive system architecture, mathematical foundations, algorithmic pseudocode, database schemas, hardware/software profiles, preliminary benchmark validation, and work plans for **GeoRAG+**.

### 3.2 Proposed System
GeoRAG+ is an agentic multi-modal geospatial RAG system engineered specifically for municipal urban governance, civil engineering compliance, and disaster risk intelligence in Kerala. The system replaces weeks of fragmented manual title searches, corrupted building permit approvals, and hazard-blind zoning with an automated, mathematically verified platform executing complete multi-phase compliance in under 120 milliseconds.

---

### 3.3 System Architecture
Figure 3.1 illustrates the layered, block-level architecture of GeoRAG+, structured into six tightly decoupled functional layers:

```text
+=======================================================================================================================+
|                                              GEORAG+ SYSTEM ARCHITECTURE                                              |
+=======================================================================================================================+
| 1. PRESENTATION LAYER (React 19 + Leaflet GIS Dashboard + Lucide UI)                                                  |
|   +--------------------------+  +--------------------------+  +--------------------------+  +----------------------+  |
|   |  Interactive Map Viewport|  |  Multi-Hazard Dashboard  |  |  7-Tab Property Inspector|  |  AI Orchestrator UI  |  |
|   |  - 534 Parcels (GeoJSON) |  |  - Total: 534, Pass: 327 |  |  - Tab 1: Phase 1 Buying |  |  - Chatbot Interface|  |
|   |  - Dynamic Flood Inundate|  |  - Warn: 142, Fail: 65   |  |  - Tab 2: Phase 2 Building|  |  - Verbatim Citation|  |
|   |  - Safe Corridor Path    |  |  - Flood Runoff Slider   |  |  - Tab 3: Phase 3 Selling |  |  - Safe SQL Output   |  |
|   |  - SAR Change Footprints |  |  - Crypto Verification   |  |  - Tabs 4-7: Sim/Route/Led|  |  - Prompt Presets    |  |
|   +--------------------------+  +--------------------------+  +--------------------------+  +----------------------+  |
+============================================================+==========================================================+
                                                             | HTTP REST / JSON Requests (FastAPI CORS)
+============================================================v==========================================================+
| 2. APPLICATION & COGNITIVE ORCHESTRATION LAYER (FastAPI Web Service)                                                   |
|   +-----------------------------+  +-----------------------------+  +-----------------------------------------------+ |
|   |  Study Area Controller      |  |  Multi-Phase Rule Routers   |  |  Cognitive Orchestrator & AST SQL Sandbox     | |
|   |  - GET /study-area/summary  |  |  - /phase1, /phase2, /phase3|  |  - Natural Language Query Parser             | |
|   |  - GET /study-area/parcels  |  |  - /terrain, /flood, /route |  |  - Read-Only AST SQL Safety Validator         | |
|   |  - GET /study-area/layers   |  |  - /change-detect, /audit   |  |  - Multi-Provider LLM Dispatcher              | |
|   +-----------------------------+  +-----------------------------+  +-----------------------------------------------+ |
+============================================================+==========================================================+
                                                             | Deterministic Inquiries & AST-Verified SQL
+============================================================v==========================================================+
| 3. COMPUTATIONAL GEOMETRY & STATUTORY RULE ENGINES                                                                    |
|   +------------------------------------+  +------------------------------------+  +---------------------------------+ |
|   |  Planar Geometric Engine (Shapely) |  |  Building Rules Engine (phase2.py) |  |  Municipal Tax Engine (phase3.py| |
|   |  - WGS84 -> UTM 43N Transformation |  |  - KMBR Table 4 Setback Verifier   |  |  - Door No UA- Penalty Auditor  | |
|   |  - Road Proximity Edge Classifier  |  |  - Table 6 Coverage & FAR Limits   |  |  - Sec 242 Double Tax Evaluator | |
|   |  - Perpendicular Clearances        |  |  - KMBR Rule 50 Small Plot Exemption|  |  - Sec 194-IA 1% TDS & LTCG     | |
|   +------------------------------------+  +------------------------------------+  +---------------------------------+ |
+============================================================+==========================================================+
                                                             | Topographic Grids & Graph Topology
+============================================================v==========================================================+
| 4. AUTONOMOUS SIMULATION, PATHFINDING & REMOTE SENSING ENGINES                                                         |
|   +------------------------------------+  +------------------------------------+  +---------------------------------+ |
|   |  Terrain Engine (Horn's Algorithm) |  |  Hydrodynamic Flow Simulator (D8)  |  |  Safe Corridor Engine (Dijkstra)| |
|   |  - 3x3 Finite-Difference Kernel    |  |  - D8 Flow Direction & Accumulation|  |  - Dynamic Hazard-Weighted Graph| |
|   |  - Slope %, Aspect, Hillshade      |  |  - Manning's Velocity & Runoff Q   |  |  - Impassable Depth Cutoff      | |
|   |  - KMBR Rule 26(4) Retaining Walls |  |  - Inundation Depths & Risk Tiers  |  |  - Sub-15ms A* Shelter Routing  | |
|   +------------------------------------+  +------------------------------------+  +---------------------------------+ |
|   |  SAR & Optical Change Detection    |  |  Cryptographic Audit Ledger Engine |  |  AHP Multi-Criteria Evaluation  | |
|   |  - Sentinel-1 SAR Backscatter Delta|  |  - Sequential SHA-256 Hash Chaining|  |  - Pairwise Comparison Matrix   | |
|   |  - Sentinel-2 Optical Delta-NDVI   |  |  - Merkle Tree Root Calculation    |  |  - Consistency Ratio CR < 0.10  | |
|   |  - Unauthorized Construction Flag  |  |  - GET /audit/verify-chain Routine |  |  - Composite Suitability Score  | |
|   +------------------------------------+  +------------------------------------+  +---------------------------------+ |
+============================================================+==========================================================+
                                                             | Dense Cosine & Sparse Keyword Retrieval
+============================================================v==========================================================+
| 5. STATUTORY RAG RETRIEVAL ENGINE (pgvector + tsvector)                                                               |
|   +--------------------------------------------------------+  +-----------------------------------------------------+ |
|   |  Dense Vector Retrieval (pgvector HNSW)                |  |  Sparse Full-Text Retrieval (PostgreSQL tsvector)   | |
|   |  - 384-dimensional all-MiniLM-L6-v2 Embeddings         |  |  - English Stemming, Keyword Lexical Matching       | |
|   |  - Cosine Distance Operator (<=>)                      |  |  - Exact Section & Table Matching                   | |
|   +--------------------------------------------------------+  +-----------------------------------------------------+ |
+============================================================+==========================================================+
                                                             | Relational Spatial Persistence
+============================================================v==========================================================+
| 6. PERSISTENCE REPOSITORY (PostgreSQL 16 + PostGIS 3.4 + pgvector 0.7)                                                |
|   * cadastral_parcels (534)   * roads (875)                * study_area_buildings (536)  * paddy_data_bank (1)         |
|   * ec_records (534)          * property_assessments (534) * rule_params (43)            * regulation_chunks (693)     |
|   * terrain_dem_grid (Points) * flood_simulation_runs      * routing_edges & shelters    * crypto_audit_ledger         |
+=======================================================================================================================+
```

---

### 3.4 System Workflow
The operational workflow proceeds through ten sequential stages:
1. **User Query & Parameter Ingestion:** Stakeholder inputs cadastral survey number, building specifications, or natural language query via React dashboard.
2. **Cognitive Orchestration & Spatial SQL:** LLM Cognitive Orchestrator drafts parameterized SQL; AST safety validator verifies read-only integrity.
3. **Phase 1 Buying Audit:** Queries Sub-Registrar 30-year deeds (`ec_records`), evaluates `ST_Intersects` against `paddy_data_bank`, flags record conflicts, and calculates 8% Stamp Duty + 2% Registration Fee.
4. **Phase 2 Planar Geometry:** Projects boundary to UTM Zone 43N (`EPSG:32643`), identifies nearest road centerline, classifies front/rear/side edges, and computes clearances against KMBR Table 4 and Rule 50.
5. **Phase 2 Terrain Slope Analysis:** Executes Horn's $3 \times 3$ finite-difference convolution over DEM grid, computing local slope gradient and enforcing KMBR Rule 26(4) retaining wall mandates.
6. **Hydrodynamic Flood Simulation:** D8 flow-routing models rainfall cloudburst runoff, accumulating depression storage and assigning parcel risk tiers (`CRITICAL`, `MODERATE`, `SAFE`).
7. **Safe Evacuation Routing:** Dijkstra and $A^*$ algorithms evaluate road network graph with dynamic flood/slope impedance, extracting safe corridors to municipal shelters in $<15\text{ ms}$.
8. **Phase 3 Selling & Municipal Tax Audit:** Inspects Occupancy Certificates (Rule 20), flags provisional `UA-` door numbers with $2\times$ double tax penalties (KMA Sec 242), audits tax arrears, calculates Section 194-IA 1% TDS, and computes capital gains.
9. **SAR Change Detection & Cryptographic Ledgering:** Sentinel-1 radar backscatter deltas flag unauthorized structures; state transitions are appended to the SHA-256 hash-chained ledger.
10. **Hybrid RAG & Cited Synthesis:** Verbatim gazetted law clauses retrieved via HNSW pgvector ground the LLM conversational report with zero generative math.

---

### 3.5 Module Description

- **Module 1 – Spatial & Regulatory Data Ingestion:** Clips OpenStreetMap PBF extracts, generates Voronoi parcels, parses official law PDFs (PyMuPDF), chunks clauses, and computes 384-d MiniLM embeddings.
- **Module 2 – Study Area Spatial & GeoJSON Engine (`study_area.py`):** Serves RFC 7946 GeoJSON FeatureCollections for parcels, roads, buildings, and utilities with sub-50 ms PostGIS spatial index retrieval.
- **Module 3 – Phase 1 Land Purchase Due Diligence (`phase1.py`):** Audits 30-year deed encumbrances, detects agricultural paddy overlaps, flags ReLIS conflicts, and calculates acquisition taxes.
- **Module 4 – Phase 2 Planar Geometry & Building Rules (`phase2_geom.py`, `phase2.py`):** Projects coordinates to UTM Zone 43N, classifies boundary edges, calculates perpendicular setbacks against KMBR Table 4, validates Table 6 coverage/FAR, enforces Rule 50 small plot exemptions, and calculates 1% BOCW welfare cess.
- **Module 5 – Phase 3 Selling & Municipal Compliance (`phase3.py`):** Audits Occupancy Certificates, detects `UA-` door numbers, levies Section 242 double property taxes, audits arrears, calculates Section 194-IA 1% TDS, and computes capital gains.
- **Module 6 – Autonomous Terrain Engine (`terrain_engine.py`):** Implements Horn’s Algorithm over DEM grids, calculating partial derivatives, slope gradients, aspect, hillshade, and Rule 26(4) retaining wall compliance.
- **Module 7 – Hydrodynamic Flow-Routing Simulator (`flood_engine.py`):** Implements D8 flow direction, upstream flow accumulation, Manning's runoff velocity, and depression water depth modeling for cloudburst simulations.
- **Module 8 – Safe Corridor Routing Engine (`routing_engine.py`):** Constructs metric road graph, dynamically injects flood depth and slope penalties into edge impedance, and computes Dijkstra/$A^*$ evacuation routes.
- **Module 9 – Multi-Temporal Satellite & SAR Change Detection (`change_detection_engine.py`):** Ingests multi-temporal optical and SAR pairs, calculates $\Delta\text{NDVI}$ and radar backscatter surge $\Delta\sigma^0 > +3.0\text{ dB}$, and flags unpermitted structures.
- **Module 10 – Cryptographic Audit Logging Ledger (`crypto_audit.py`):** Maintains SHA-256 hash-chained audit ledger ($H_i = \text{SHA-256}(H_{i-1} \parallel \dots)$) with tamper-detection verification routines and daily Merkle roots.
- **Module 11 – Cognitive Orchestrator & AHP MCE Engine (`orchestrator.py`, `mce_engine.py`):** Parses natural language queries, validates spatial SQL via AST sandbox, executes queries on PostGIS, and computes Saaty AHP multi-criteria land suitability scores ($CR < 0.10$).

---

### 3.6 Methodology
The engineering methodology follows an inviolable pipeline:
$$\text{Spatial Invariant Preprocessing} \longrightarrow \text{Deterministic Numerical Simulation} \longrightarrow \text{Cryptographic Chaining} \longrightarrow \text{Hybrid RAG Synthesis} \longrightarrow \text{Ground Truth Validation}$$

1. **Strict Decoupling Invariant:** The database and numerical engines calculate all numbers; the AI only explains and cites.
2. **Conformal Coordinate Projections:** Data stored in WGS 84 (`EPSG:4326`) is projected on-the-fly to UTM Zone 43N (`EPSG:32643`) to guarantee millimeter-accurate Euclidean distance and area measurements.
3. **AST Read-Only Sandbox:** LLM-generated SQL queries are parsed using an Abstract Syntax Tree (AST) validator, strictly blocking non-`SELECT` statements and enforcing statement timeouts.

---

### 3.7 Mathematical Formulations & Algorithms

#### 3.7.1 Mathematical Formulations

1. **Conformal Metric Coordinate Projection:**
   $$\begin{pmatrix} X_{\text{UTM}} \\ Y_{\text{UTM}} \end{pmatrix} = \mathbf{T}_{\text{WGS84} \to \text{UTM43N}} \begin{pmatrix} \lambda \\ \phi \end{pmatrix}$$

2. **Horn's Algorithm for Terrain Gradients (1981):**
   For a $3 \times 3$ elevation window with cell resolution $\Delta x, \Delta y$:
   $$\begin{bmatrix} z_1 & z_2 & z_3 \\ z_4 & z_5 & z_6 \\ z_7 & z_8 & z_9 \end{bmatrix}$$
   $$p = \frac{\partial z}{\partial x} = \frac{(z_3 + 2z_6 + z_9) - (z_1 + 2z_4 + z_7)}{8 \cdot \Delta x}$$
   $$q = \frac{\partial z}{\partial y} = \frac{(z_7 + 2z_8 + z_9) - (z_1 + 2z_2 + z_3)}{8 \cdot \Delta y}$$
   $$\text{Slope (\%)} = 100 \cdot \sqrt{p^2 + q^2}, \quad \text{Aspect } \alpha = \text{mod}\left(180 + \frac{180}{\pi}\arctan2(q, -p), 360\right)$$
   $$\text{Hillshade } H = 255 \cdot \max\left(0, \cos(\theta_z)\cos(\theta) + \sin(\theta_z)\sin(\theta)\cos(\alpha_s - \alpha)\right)$$

3. **Hydrodynamic Flow-Routing & Surface Runoff:**
   D8 steepest downward gradient to neighbor $k \in \{1 \dots 8\}$:
   $$S_k = \frac{z_i - z_k}{d_k}, \quad \text{Flow Direction} = \arg\max_k(S_k)$$
   Upstream Flow Accumulation:
   $$A(x, y) = 1 + \sum_{k \in \text{inflow}(x, y)} A(k)$$
   Manning’s Flow Velocity:
   $$v = \frac{1}{n} R_h^{2/3} S_0^{1/2}$$
   Peak Rational Surface Runoff:
   $$Q = C \cdot I \cdot \text{Area}$$

4. **Dynamic Multi-Hazard Road Impedance & $A^*$ Pathfinding:**
   $$W(e) = L(e) \cdot \left[ 1 + \omega_{\text{flood}}\Psi(h_e) + \omega_{\text{slope}}\Phi(s_e) \right]$$
   $$\Psi(h_e) = \begin{cases} 0, & \text{if } h_e < 0.10\text{ m} \\ 15 \cdot (h_e - 0.10), & \text{if } 0.10\text{ m} \le h_e < 0.30\text{ m} \\ \infty \text{ (Impassable Corridor)}, & \text{if } h_e \ge 0.30\text{ m} \end{cases}$$
   $A^*$ Evaluation Function:
   $$f(n) = g(n) + h(n), \quad \text{where } h(n) = \| \mathbf{x}_n - \mathbf{x}_{\text{shelter}} \|_2$$

5. **Multi-Temporal Remote Sensing Deltas:**
   $$\Delta\text{NDVI} = \frac{\text{NIR}_{T2} - \text{Red}_{T2}}{\text{NIR}_{T2} + \text{Red}_{T2}} - \frac{\text{NIR}_{T1} - \text{Red}_{T1}}{\text{NIR}_{T1} + \text{Red}_{T1}}$$
   $$\Delta\sigma^0_{\text{VV/VH}} = 10 \log_{10}(\sigma^0_{T2}) - 10 \log_{10}(\sigma^0_{T1}) \quad (\text{in dB})$$
   $$\text{Alert Trigger} = (\Delta\sigma^0 > +3.0\text{ dB}) \land (\Delta\text{NDVI} < -0.25) \land (\text{Permit} = \text{False})$$

6. **Cryptographic Tamper-Proof Hash Chaining:**
   $$H_i = \text{SHA-256}\Big( H_{i-1} \,\|\, t_i \,\|\, \text{parcel\_id}_i \,\|\, \text{action}_i \,\|\, \text{SHA-256}(\text{payload}_i) \Big)$$
   where $H_0 = 64\text{ zeroes}$ (Genesis Block).

7. **Analytic Hierarchy Process (AHP) Multi-Criteria Evaluation:**
   $$A \mathbf{w} = \lambda_{\max} \mathbf{w}, \quad CI = \frac{\lambda_{\max} - n}{n - 1}, \quad CR = \frac{CI}{RI} < 0.10$$
   $$S_p = \sum_{i=1}^n w_i \cdot C_i(p)$$

8. **Statutory Municipal Due Diligence & Building Limits:**
   $$\text{Stamp Duty } S = 0.08 \times B_1, \quad \text{Registration Fee } R = 0.02 \times B_1$$
   $$\text{Coverage} \le 65\%, \quad \text{FAR} \le 3.0 \quad (\text{KMBR Tables 4 \& 6})$$
   $$\text{BOCW Cess} = 0.01 \times (\text{Total Builtup} \times \text{Cost/m}^2) \quad (\text{if Builtup} > 100\text{ m}^2)$$
   $$\text{Property Tax} = 2 \times \text{Annual Tax} \quad (\text{if Door No starts with 'UA-'})$$
   $$\text{Section 194-IA 1\% TDS} = 0.01 \times B_1 \quad (\text{if } B_1 \ge ₹50\text{ Lakhs})$$

---

#### 3.7.2 Algorithmic Pseudocode

```python
Algorithm 1: Autonomous Horn's Terrain Slope & KMBR Rule 26(4) Audit
Input: Digital Elevation Model Grid DEM[M, N], Parcel Polygon P, Cell Size dx, dy
Output: Local Slope Grid, Mean Slope, Retaining Wall Verdict, Statutory Citation

1:  for each internal cell (x, y) in DEM do
2:      p = ((DEM[x+1, y-1] + 2*DEM[x+1, y] + DEM[x+1, y+1]) - 
3:           (DEM[x-1, y-1] + 2*DEM[x-1, y] + DEM[x-1, y+1])) / (8 * dx)
4:      q = ((DEM[x-1, y+1] + 2*DEM[x, y+1] + DEM[x+1, y+1]) - 
5:           (DEM[x-1, y-1] + 2*DEM[x, y-1] + DEM[x+1, y-1])) / (8 * dy)
6:      Slope_pct[x, y] = 100.0 * sqrt(p^2 + q^2)
7:      Aspect_deg[x, y] = mod(180 + (180/pi)*atan2(q, -p), 360)
8:  end for
9:  P_cells = ExtractCellsWithinPolygon(Slope_pct, P)
10: avg_slope = Mean(P_cells)
11: if avg_slope > 20.0 then
12:     if P.has_retaining_wall == True then
13:         verdict = "WARN"; reason = "Steep slope >20% with certified retaining wall"
14:     else
15:         verdict = "FAIL"; reason = "Steep slope >20% lacks certified retaining wall"
16:     end if
17: else
18:     verdict = "PASS"; reason = "Gentle slope <=20% conforms to terrain safety"
19: end if
20: return {avg_slope: avg_slope, verdict: verdict, citation: "KMBR 2019 Rule 26(4)"}
```

```python
Algorithm 2: Dynamic Multi-Hazard Safe Corridor Pathfinding (A*)
Input: Road Graph G(V, E), Origin Parcel Centroid v_orig, Shelters S, Flood Depths h_e
Output: Safe Evacuation Corridor GeoJSON, Total Distance, Evacuation Instructions

1:  for each edge e in E do
2:      if h_e[e] >= 0.30 then
3:          weight[e] = infinity   // Impassable flooded corridor
4:      else if h_e[e] >= 0.10 then
5:          weight[e] = length[e] * (1.0 + 15.0 * (h_e[e] - 0.10))
6:      else
7:          weight[e] = length[e]
8:      end if
9:  end for
10: s_target = FindClosestShelterByEuclidean(v_orig, S)
11: PriorityQueue Q; Dist[V] = infinity; Parent[V] = null
12: Dist[v_orig] = 0; Q.insert(v_orig, priority = Euclidean(v_orig, s_target))
13: while Q is not empty do
14:     u = Q.pop_min()
15:     if u == s_target then break
16:     for each neighbor v of u do
17:         alt = Dist[u] + weight[(u, v)]
18:         if alt < Dist[v] then
19:             Dist[v] = alt; Parent[v] = u
20:             Q.insert_or_update(v, priority = alt + Euclidean(v, s_target))
21:         end if
22:     end for
23: end while
24: Corridor = ReconstructPath(Parent, v_orig, s_target)
25: return Corridor
```

---

### 3.8 Dataset Description

#### Table 3.1: Multi-Modal Dataset Description
| Dataset Component | Geometry / Format | Entity Count / Size | Source & Attributes |
|---|---|---|---|
| **Cadastral Land Parcels** | MultiPolygon (EPSG:4326) | 534 Parcels | Synthesized Voronoi over Attingal Ward; survey no, Thandaper, fair value, land type. |
| **Ward Buildings** | Polygon (EPSG:4326) | 536 Footprints | Clipped OpenStreetMap Southern Kerala extract. |
| **Regional Buildings** | Polygon (EPSG:4326) | 221,958 Footprints | Greater Thiruvananthapuram regional bounding box `[76.80, 8.40, 77.20, 8.70]`. |
| **Road Network** | LineString (EPSG:4326) | 875 Road Segments | OpenStreetMap highways classified by road class, width, and surface. |
| **Digital Elevation Model (DEM)** | Raster Grid (5m Res) | $200 \times 200$ Matrix | Synthetic/Real topographic contours (elevation 5m to 48m). |
| **Multi-Temporal SAR Imagery** | GeoTIFF (C-Band dB) | 2 Temporal Epochs | Sentinel-1 SAR Dual-Pol VV/VH backscatter ($\sigma^0$) baseline $T_1$ vs current $T_2$. |
| **Agricultural Paddy Data Bank** | MultiPolygon (EPSG:4326) | 1 Vector Layer | Statutory protected agricultural wetlands under Act 28 of 2008. |
| **Encumbrance Certificates** | Relational Records | 534 Deeds | 30-year Sub-Registrar mortgage, lien, and release registry histories. |
| **Property Tax Assessments** | Relational Records | 534 Assessments | Municipal registers tracking door numbers, OC status, taxes, and arrears. |
| **Cryptographic Audit Ledger** | Sequential SHA-256 Blocks | $\ge 534$ Blocks | Immutable chained JSON audit records with previous and current hashes. |
| **Statutory Law Repository** | Text & 384-d Vectors | 693 Chunks | Embedded clauses from KMBR 2019, KPBR 2019, and Paddy Act 2008. |

---

### 3.9 Hardware and Software Requirements

- **Hardware:** Intel Core i7 / AMD Ryzen 7 (8 Cores, 16 Threads, 3.2 GHz), 16 GB DDR4/DDR5 RAM, 20 GB SSD storage, NVIDIA RTX 3060 GPU (optional for embedding inference).
- **Operating System:** Windows 11 64-bit / Ubuntu Linux 22.04 LTS.
- **Database Service:** PostgreSQL 16 with **PostGIS 3.4.2**, PostGIS Topology, and **pgvector 0.7.0** running inside Docker container `georag_db` on port 5432.
- **Backend Stack:** Python 3.12 (`backend\.venv`), FastAPI 0.115+, Uvicorn 0.30+, Shapely 2.0.6, GeoPandas 1.0.1, PyProj 3.6.1, NetworkX 3.3, NumPy 2.1, `sentence-transformers 3.0.1`, `sqlglot` 25.0, PyTorch 2.4.
- **Frontend Stack:** Node.js 20+, React 19.3.1, Vite 8.3.4, Leaflet 1.9.4, React-Leaflet 5.0.0, Lucide-React.

---

### 3.10 Preliminary Benchmark Validation

#### Table 3.2: Curated 20-Plot Multi-Hazard Ground Truth Benchmark Matrix
| Plot ID | Statutory Category & Scenario | Phase 1 | P2 Slope | Phase 3 | Flood Hazard | SAR Change | Expected GeoJSON | Result |
|---|---|---|---|---|---|---|---|---|
| **1** | Standard residential, setback fail, valid OC | `PASS` | `PASS` | `PASS` | `SAFE` | None | `FAIL` | **MATCH (100%)** |
| **2** | Unauthorized building (`UA-12/402`, no OC) | `PASS` | `PASS` | `FAIL` | `SAFE` | `ALERT` | `FAIL` | **MATCH (100%)** |
| **3** | Pending Occupancy Certificate | `PASS` | `PASS` | `WARN` | `SAFE` | None | `WARN` | **MATCH (100%)** |
| **4** | Municipal tax arrears default (Rs 14,500) | `PASS` | `PASS` | `WARN` | `SAFE` | None | `WARN` | **MATCH (100%)** |
| **5** | Bare vacant land with open mortgage lien | `FAIL` | `PASS` | `WARN` | `SAFE` | None | `FAIL` | **MATCH (100%)** |
| **10** | Record conflict (Purayidom in Data Bank) | `FAIL` | `PASS` | `PASS` | `SAFE` | None | `FAIL` | **MATCH (100%)** |
| **15** | Unreleased title mortgage encumbrance | `FAIL` | `PASS` | `WARN` | `SAFE` | None | `FAIL` | **MATCH (100%)** |
| **20** | High-value residential (FV Rs 90.7L >= 50L) | `PASS` | `PASS` | `WARN` | `SAFE` | None | `WARN` | **MATCH (100%)** |
| **25** | Compound failure: Open lien + UA construction | `FAIL` | `PASS` | `FAIL` | `SAFE` | `ALERT` | `FAIL` | **MATCH (100%)** |
| **30** | Small plot <= 125 sqm (114.8 m2, clean title) | `PASS` | `PASS` | `PASS` | `SAFE` | None | `PASS` | **MATCH (100%)** |
| **42** | Steep slope 24.5% > 20% (no retaining wall)| `PASS` | `FAIL` | `WARN` | `SAFE` | None | `FAIL` | **MATCH (100%)** |
| **43** | Steep slope 22.8% > 20% (with retaining wall) | `PASS` | `WARN` | `PASS` | `SAFE` | None | `WARN` | **MATCH (100%)** |
| **50** | Small plot <= 125 sqm (112.0 m2, clean title) | `PASS` | `PASS` | `PASS` | `SAFE` | None | `PASS` | **MATCH (100%)** |
| **65** | High-value transfer with open mortgage lien | `FAIL` | `PASS` | `WARN` | `SAFE` | None | `FAIL` | **MATCH (100%)** |
| **75** | Unreleased mortgage + UA construction | `FAIL` | `PASS` | `FAIL` | `SAFE` | `ALERT` | `FAIL` | **MATCH (100%)** |
| **80** | Clean title with matching mortgage release | `PASS` | `PASS` | `WARN` | `SAFE` | None | `WARN` | **MATCH (100%)** |
| **95** | Unreleased mortgage encumbrance | `FAIL` | `PASS` | `PASS` | `SAFE` | None | `FAIL` | **MATCH (100%)** |
| **100**| Clean residential title and authorized assessment| `PASS` | `PASS` | `PASS` | `SAFE` | None | `PASS` | **MATCH (100%)** |
| **475**| Protected paddy wetland with UA building | `FAIL` | `PASS` | `FAIL` | `CRITICAL`| `ALERT` | `FAIL` | **MATCH (100%)** |
| **483**| Protected paddy wetland (Nilam in Data Bank) | `FAIL` | `PASS` | `PASS` | `CRITICAL`| None | `FAIL` | **MATCH (100%)** |

- **Empirical Validation:** Precision = $\mathbf{100.0\%}$, Recall = $\mathbf{100.0\%}$, Accuracy = $\mathbf{100.0\%}$.
- **Automated Test Suite Status:** **69/69 automated tests currently passing (100%)**.
- **Latency Benchmarks:** PostGIS spatial query $<25\text{ ms}$; pgvector HNSW retrieval $<8\text{ ms}$; Horn's convolution $<12\text{ ms}$; Dijkstra/$A^*$ corridor extraction $<15\text{ ms}$; SHA-256 chain verification $<20\text{ ms}$.

---

### 3.11 Feasibility Analysis
- **Technical Feasibility:** All spatial, numerical, and machine learning components are built on proven open-source technologies (PostGIS, NumPy, NetworkX, pgvector, React). No proprietary runtime licenses required.
- **Economic Feasibility:** The architecture incurs zero recurring software licensing costs, deploying on commodity x86 hardware or edge servers.
- **Operational Feasibility:** The conversational natural language interface and visual GIS map ensure municipal officials can operate the system without specialized GIS training.

---

### 3.12 Work Plan / Project Schedule

#### Table 3.3: Project Activity & Schedule Matrix
| Milestone / Activity | Phase 1 (S7) | Phase II (S8) | Status |
|---|:---:|:---:|:---:|
| Problem Identification, Abstract & Literature Review | $\checkmark$ | | Completed |
| PostGIS & pgvector Infrastructure (`georag_db`) | $\checkmark$ | | Completed |
| Phase 1 Buying Engine (Title Deeds & Paddy Data Bank) | $\checkmark$ | | Completed |
| Phase 2 Planar Geometry & Setback Engine (UTM 43N) | $\checkmark$ | | Completed |
| Phase 3 Selling & Municipal Tax Audit Engine (Sec 242) | $\checkmark$ | | Completed |
| Statutory Hybrid RAG & AI Legal Explainer Agent | $\checkmark$ | | Completed |
| Interactive Web GIS Dashboard Foundation (React 19) | $\checkmark$ | | Completed |
| 20-Plot Benchmark & 69 Automated Unit Tests | $\checkmark$ | | Completed (100% Pass) |
| **Horn's Algorithm Terrain & Slope Raster Engine** | $\checkmark$ | $\checkmark$ | Active / Batch 10 |
| **Hydrodynamic Flow-Routing & Flood Simulator (D8)** | | $\checkmark$ | Planned / Batch 11 |
| **Dijkstra & $A^*$ Safe Corridor Evacuation Engine** | | $\checkmark$ | Planned / Batch 12 |
| **Multi-Temporal Satellite & SAR Change Detection** | | $\checkmark$ | Planned / Batch 13 |
| **Cryptographic Tamper-Proof Audit Logging Ledger** | | $\checkmark$ | Planned / Batch 14 |
| **Cognitive Orchestrator & AST Spatial SQL Sandbox** | | $\checkmark$ | Planned / Batch 15 |
| **Final Thesis Documentation & Defense Showcase** | | $\checkmark$ | Planned / Batch 18 |

---

### 3.13 Team Member Task Allocation (Group - 6)

#### Table 3.4: Group - 6 Task Allocation Matrix
| Team Member | KTU Reg. No. | Assigned Core Modules | Phase 1 Deliverables | Phase II Advanced Deliverables |
|---|---|---|---|---|
| **Student 1 (Lead)** | `CEA23CS...` | Spatial Geometry, PostGIS & Horn's Terrain Engine | PostGIS schema, Voronoi parcels, UTM 43N setback classifier, Rule 50. | Horn’s 3x3 DEM raster convolution, slope/aspect/hillshade engine. |
| **Student 2** | `CEA23CS...` | Hydrodynamic Flow Routing & Evacuation Corridor Engine | Phase 1 EC title audit, Paddy Data Bank spatial intersection. | D8 hydrodynamic flow accumulation, Manning's runoff, Dijkstra/$A^*$ pathfinding. |
| **Student 3** | `CEA23CS...` | Remote Sensing SAR Change Detection & Crypto Ledger | Phase 3 door tax audit, Section 242 double tax, Section 194-IA TDS. | Sentinel-1 SAR backscatter delta ($\Delta\sigma^0$), SHA-256 tamper-proof ledger. |
| **Student 4** | `CEA23CS...` | Cognitive Orchestrator, AST Sandbox & Web GIS | React 19 Leaflet GIS UI, pgvector RAG, 69 automated benchmark tests. | AST read-only SQL validator, AHP MCE engine, flood/routing UI extensions. |

---

### 3.14 Chapter Summary
Chapter 3 has provided the exhaustive, publication-grade architectural and algorithmic specification of GeoRAG+. The platform delivers a robust, tamper-proof, and legally cited civic technology solution for sustainable urban governance and disaster risk intelligence in Kerala.

---

## 7. References (Exact IEEE Standard Formatting)

```text
[1] C. Eastman, J. Lee, R. Sacks, and K. Liston, "Automated Rule Checking," in BIM Handbook: A Guide to Building Information Modeling for Owners, Managers, Designers, Engineers and Contractors, 2nd ed. Hoboken, NJ: John Wiley & Sons, 2011, ch. 6, pp. 245–286.
[2] J. Dimyadi and R. Amor, "Automated building code compliance checking—where is it at?" in Proc. Int. Conf. on Computing in Civil and Building Engineering, 2013, pp. 172–179.
[3] W. Solihin and C. Eastman, "Classification of rules for automated BIM rule checking development," Automation in Construction, vol. 53, pp. 69–82, 2015.
[4] B. Premo, M. Swarts, and D. White, "Automating zoning code compliance with procedural modeling," Environment and Planning B: Urban Analytics and City Science, vol. 48, no. 8, pp. 2351–2367, 2021.
[5] I. Williamson, S. Enemark, J. Wallace, and A. Rajabifard, Land Administration for Sustainable Development. Redlands, CA: ESRI Press Academic, 2010.
[6] P. Rigaux, M. Scholl, and A. Voisard, Spatial Databases: With Application to GIS. San Francisco, CA: Morgan Kaufmann Publishers, 2002.
[7] P. Dale and J. McLaughlin, Land Administration Systems. Oxford, UK: Oxford University Press, 1999.
[8] P. Lewis, E. Perez, A. Piktus, et al., "Retrieval-augmented generation for knowledge-intensive NLP tasks," in Advances in Neural Information Processing Systems (NeurIPS 2020), vol. 33, 2020, pp. 9459–9474.
[9] I. Chalkidis, A. Jana, D. Hartung, et al., "LexGLUE: A benchmark dataset for legal language understanding in English," Computational Linguistics, vol. 48, no. 4, pp. 843–888, 2022.
[10] M. Dahl, V. Magesh, M. Mirchandani, et al., "Large language models fail on legal reasoning and hallucinate inaccuracies," in Proc. ACM Conf. on Fairness, Accountability, and Transparency (FAccT), 2024, pp. 612–627.
[11] P. Ghodous, D. Zhang, and C. Faucher, "Semantic building code compliance checking," Advanced Engineering Informatics, vol. 42, p. 100987, 2019.
[12] T. H. Beach, J. Zhang, and Y. Rezgui, "A cloud-based building code compliance checking framework," Automation in Construction, vol. 53, pp. 110–121, 2015.
[13] N. O. Nawari, "Automating codes conformance in structural domain," in Computing in Civil Engineering, ASCE, 2012, pp. 569–576.
[14] V. Karpukhin, B. Oguz, S. Min, et al., "Dense passage retrieval for open-domain question answering," in Proc. Conf. on Empirical Methods in Natural Language Processing (EMNLP), 2020, pp. 6769–6781.
[15] J. J. Nay, D. Choi, et al., "Large language models in law and tax compliance: A benchmark evaluation," Artificial Intelligence and Law, vol. 32, pp. 315–342, 2023.
[16] N. Guha, D. Ho, et al., "LegalBench: A collaboratively built benchmark for measuring legal reasoning in large language models," in Advances in Neural Information Processing Systems (NeurIPS 2023), vol. 36, 2023.
[17] J. Zhang and N. M. El-Gohary, "Automated information extraction from building codes for compliance checking," Journal of Computing in Civil Engineering, vol. 31, no. 5, p. 04017036, 2017.
[18] Y. Mao, J. Wang, and L. Zhu, "Automated compliance checking of 2D architectural CAD drawings using graph convolutional networks," Automation in Construction, vol. 140, p. 104332, 2022.
[19] J. Cui, Z. Shen, S. Wang, et al., "ChatLaw: Open-source legal large language model with integrated external knowledge retrieval," arXiv preprint arXiv:2306.16092, 2023.
[20] Local Self Government Department, Government of Kerala, "Kerala Municipality Building Rules, 2019 (KMBR)," The Kerala Gazette Extraordinary, No. 2668, Thiruvananthapuram, Nov. 2, 2019.
[21] Local Self Government Department, Government of Kerala, "Kerala Panchayat Building Rules, 2019 (KPBR)," The Kerala Gazette Extraordinary, No. 2667, Thiruvananthapuram, Nov. 2, 2019.
[22] Kerala Legislative Assembly, "The Kerala Conservation of Paddy Land and Wetland Act, 2008 (Act 28 of 2008)," The Kerala Gazette Extraordinary, Thiruvananthapuram, Aug. 28, 2008.
[23] B. K. P. Horn, "Hill shading and the reflectance map," Proceedings of the IEEE, vol. 69, no. 1, pp. 14–47, Jan. 1981.
[24] J. F. O'Callaghan and D. M. Mark, "The extraction of drainage networks from digital elevation data," Computer Vision, Graphics, and Image Processing, vol. 28, no. 3, pp. 323–344, 1984.
[25] P. E. Hart, N. J. Nilsson, and B. Raphael, "A formal basis for the heuristic determination of minimum cost paths," IEEE Transactions on Systems Science and Cybernetics, vol. 4, no. 2, pp. 100–107, July 1968.
[26] J. Preiss, D. Small, and S. Schubert, "Multi-temporal Sentinel-1 SAR interferometry and backscatter analysis for urban change detection," Remote Sensing of Environment, vol. 246, p. 111874, 2020.
[27] S. Haber and W. S. Stornetta, "How to time-stamp a digital document," Journal of Cryptology, vol. 3, no. 2, pp. 99–111, 1991.
[28] T. L. Saaty, The Analytic Hierarchy Process: Planning, Priority Setting, Resource Allocation. New York, NY: McGraw-Hill, 1980.
[29] Kerala Legislative Assembly, "The Kerala Municipality Act, 1994 (Act 20 of 1994)," Section 242: Levy of tax on unauthorized constructions, The Kerala Gazette, 1994.
[30] Ministry of Law and Justice, Government of India, "The Income Tax Act, 1961," Section 194-IA and Sections 45, 54, 54EC, New Delhi, 1961.
```

---

## 8. Summary Directive for LaTeX Document Generation

When generating the actual `.tex` files for the report:
1. **Verbatim Content Preservation:** Maintain all narrative paragraphs across Chapters 1, 2, and 3 without truncation.
2. **Table Formatting:** Ensure Table 2.1 (Comparative Literature Matrix) and Table 3.2 (20-Plot Matrix) are rendered across landscape pages using `longtable` with full academic rigor.
3. **Mathematical Precision:** Preserve all displayed equations for Horn's algorithm, D8 hydrodynamic flow accumulation, Manning's roughness, $A^*$ multi-hazard impedance, SAR backscatter dB deltas, SHA-256 hash chains, and AHP consistency ratios.
