# DB Upgrade Impact Analysis & Validation AI Agent

An enterprise-grade deterministic + Multi-Agent platform that analyzes official DBMS vendor upgrade documentation and validates the actual upgrade impact on target database parameters, schemas, stored objects, and application SQL workloads.

- **MVP Target**: **MySQL 8.0 → MySQL 8.4** version upgrade impact analysis & validation.
- **Extensibility Target**: Designed with pluggable DBMS adapters (`backend/app/adapters/`) for future expansion to **MariaDB**, **PostgreSQL**, and **Oracle**.

---

## 1. Key Capabilities

1. **Official Vendor Documentation Analysis**: Hybrid RAG (`pgvector` + keyword search) with Corrective Retrieval (CRAG) strictly restricted to official vendor domains (`dev.mysql.com`, `downloads.mysql.com`).
2. **Parameter Change Impact Validation**: Deterministic **Parameter Rule Engine** identifying removed, deprecated, default-changed, and range-modified system variables.
3. **Schema & Stored Object Compatibility Validation**: Deterministic **Schema Validator** checking reserved words, character sets (`utf8mb3`/`utf8mb4`), obsolete data types, authentication plugins, and stored routines.
4. **Application SQL Static Analysis**: AST-based static SQL validation powered by **SQLGlot**.
5. **DBA Action Guide Generation**: Pre-upgrade, during-upgrade, and post-upgrade DBA runbooks grounded in official citations.
6. **Application SQL Remediation & Verification Request Generation**: Candidate rewritten SQL comparisons via **Monaco Diff Editor** and structured Verification Request packages (never auto-executed on target DBs).
7. **Dual Collection Modes**: Supports both **Read-Only Direct DB Connection** and **Offline File Upload** normalized into a single **Unified Inventory Model**.
8. **Offline Collector Scripts & Format Guides**: Ready-to-run diagnostic SQL scripts and upload specifications in `collectors/`.
9. **Validation History & Re-validation Management**: Historical snapshot tracking and Run $N$ vs. Run $N+1$ remediation diffing.
10. **Strict Evidence Validation**: Every verdict requires official documentation evidence (`Evidence Validator`). **If official documentation evidence is insufficient, an item is never judged as normal (`PASS`).**

---

## 2. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React, TypeScript, Vite, Tailwind CSS, shadcn/ui, TanStack Query, Monaco Diff Editor |
| **Backend** | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic |
| **AI & RAG** | LangChain DeepAgents, LangGraph, Hybrid RAG, Corrective Retrieval, Structured Outputs, LangSmith |
| **Validation** | SQLGlot, Deterministic Parameter Rule Engine, Schema Validator, Evidence Validator |
| **Storage** | PostgreSQL 16 + `pgvector` |
| **Infrastructure** | Docker Compose |

---

## 3. Repository Structure

```text
AIDBUpgrade/
├── AGENTS.md                 # Persistent architecture, security, and engineering rules
├── README.md                 # Project overview and execution guide
├── .env.example              # Environment configuration template
├── docker-compose.yml        # PostgreSQL + pgvector & application container definitions
├── frontend/                 # React + TypeScript + Vite SPA
├── backend/                  # FastAPI + Validation Engines + Multi-Agent Backend
│   ├── alembic/              # Database migrations
│   ├── app/                  # 16 mandatory domain/layer packages
│   │   ├── api/              # FastAPI HTTP/SSE routers
│   │   ├── core/             # Config, security, encryption, logging, DB session
│   │   ├── schemas/          # Pydantic v2 models & Unified Inventory Model
│   │   ├── services/         # Application domain services
│   │   ├── repositories/     # SQLAlchemy 2 & pgvector data access layer
│   │   ├── orchestration/    # LangGraph multi-agent workflows
│   │   ├── agents/           # LangChain DeepAgents definitions
│   │   ├── rag/              # Hybrid RAG & Corrective Retrieval
│   │   ├── rules/            # Deterministic upgrade rule catalogs
│   │   ├── validators/       # SQLGlot, Parameter, Schema, and Evidence validators
│   │   ├── adapters/         # DBMS-specific implementations (MVP: mysql/)
│   │   ├── collection/       # Direct DB & Offline File -> Unified Inventory pipeline
│   │   ├── tools/            # Sandboxed read-only agent tools
│   │   ├── mcp/              # Model Context Protocol integrations
│   │   ├── history/          # Validation run history & re-validation diffing
│   │   └── workers/          # Background jobs
│   └── tests/                # Automated test suite & explicit test fixtures
├── collectors/               # Offline SQL collection scripts & format guides
├── skills/                   # Domain-specific agent skills
├── docs/                     # System architecture, requirements, and development plan
└── infra/                    # Dockerfiles & PostgreSQL/pgvector init scripts
```

---

## 4. Getting Started & Execution Guide

### Prerequisites
- **Docker** & **Docker Compose** (v2+)
- **Python 3.12+**
- **Node.js 20+ / 22+** & **npm**

### Step 1: Configure Environment Variables
Copy `.env.example` to `.env` and populate the required values:

```bash
cp .env.example .env
```

### Step 2: Validate & Start Infrastructure (PostgreSQL + pgvector)
Validate the Docker Compose configuration and start the PostgreSQL + `pgvector` service:

```bash
# Validate Docker Compose syntax and resolved configuration
docker compose config

# Start PostgreSQL with pgvector extension enabled
docker compose up -d postgres

# Check database health status
docker compose ps
```

### Step 3: Run Architecture & Structure Verification Tests
```bash
python3 -m unittest discover -s backend/tests -p "test_*.py" -v
```

### Step 4: Full Application Stack (Subsequent Steps)
Once Backend (STEP 01–06) and Frontend (STEP 07) modules are implemented:
- **Backend (Local Dev)**:
  ```bash
  cd backend
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```
- **Frontend (Local Dev)**:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```
- **Full Docker Compose Stack**:
  ```bash
  docker compose --profile app up --build -d
  ```

---

## 5. Documentation & Governance

- [Persistent Agent & Engineering Rules (`AGENTS.md`)](./AGENTS.md)
- [System Architecture (`docs/ARCHITECTURE.md`)](./docs/ARCHITECTURE.md)
- [Requirements Specification (`docs/REQUIREMENTS.md`)](./docs/REQUIREMENTS.md)
- [Phased Development Plan (`docs/DEVELOPMENT_PLAN.md`)](./docs/DEVELOPMENT_PLAN.md)
