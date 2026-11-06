# AGENTS.md — Persistent Architecture, Security & Engineering Rules

This document defines the mandatory architectural principles, security guardrails, and development rules for the **DB Upgrade Impact Analysis & Validation AI Agent** project. Every AI agent and human contributor working in this repository MUST strictly adhere to these rules across all development steps.

---

## 1. Project Identity & Scope

- **Project Name**: DB Upgrade Impact Analysis & Validation AI Agent
- **Core Objective**: Analyze official vendor documentation for DBMS version upgrades and validate the actual impact on target database environments (parameters, schemas, stored objects, and application SQL) through a deterministic + Multi-Agent hybrid system.
- **MVP Target**: **MySQL 8.0 → MySQL 8.4** version upgrade analysis and validation.
- **Extensibility Target**: Architect all interfaces so **MariaDB**, **PostgreSQL**, and **Oracle** can be added cleanly via modular DBMS adapters in future phases. **Do NOT implement MariaDB, PostgreSQL, or Oracle logic during the MVP.**

---

## 2. Technology Stack Rules

### Frontend (`frontend/`)
- **Framework**: React + TypeScript + Vite
- **Styling & UI**: Tailwind CSS + shadcn/ui
- **Server State Management**: TanStack Query
- **Code & SQL Comparison**: Monaco Diff Editor

### Backend (`backend/`)
- **Runtime**: Python 3.12+ (verified compatible version)
- **Web Framework**: FastAPI
- **Data Validation & Settings**: Pydantic v2
- **ORM & Database Access**: SQLAlchemy 2.0 (async/typed declarative style)
- **Migrations**: Alembic

### AI & Orchestration
- **Agent Framework**: LangChain DeepAgents & LangGraph
- **Retrieval Architecture**: Hybrid RAG (Vector + Keyword/BM25) + Corrective Retrieval (CRAG)
- **Output Contract**: Strict Structured Outputs (Pydantic v2 schemas)
- **Observability**: LangSmith tracing

### Validation Engines
- **SQL Static Analysis**: SQLGlot
- **Parameter Validation**: Deterministic Parameter Rule Engine
- **Schema & Object Compatibility**: Deterministic Schema Validator
- **Hallucination / Citation Guard**: Evidence Validator

### Storage & Infrastructure
- **Database**: PostgreSQL with `pgvector` extension
- **Infrastructure**: Docker Compose

---

## 3. Mandatory Architectural Principles

1. **Strict Frontend / Backend Separation**:
   - `frontend/` and `backend/` are strictly decoupled and communicate exclusively via versioned REST/SSE APIs defined in `backend/app/api` and `backend/app/schemas`.

2. **Mandatory Backend Package Structure**:
   The backend (`backend/app/`) MUST maintain the following 16 domain/layer packages:
   - `api`: FastAPI routers, dependency injection, request/response handling.
   - `core`: Application configuration, logging, security/encryption utilities, exceptions, DB session management.
   - `schemas`: Pydantic v2 DTOs, API contracts, and structured AI output schemas.
   - `services`: Application business logic coordinating repositories, validators, and orchestration.
   - `repositories`: SQLAlchemy 2 data access layer (CRUD, vector/hybrid search queries).
   - `orchestration`: LangGraph workflows, state graphs, and multi-agent execution pipelines.
   - `agents`: LangChain DeepAgents definitions (Doc Analyzer, Impact Explainer, DBA Guide Generator, SQL Remediation Agent, etc.).
   - `rag`: Document ingestion, chunking, embedding, Hybrid RAG, and Corrective Retrieval pipelines.
   - `rules`: Deterministic rule definitions and evaluators (parameter changes, removed/deprecated features, reserved keywords, SQL patterns).
   - `validators`: Deterministic validation engines (`SQLGlot` AST analyzer, Parameter Rule Engine, Schema Validator, Evidence Validator).
   - `adapters`: DBMS-specific implementations isolated behind abstract interfaces (e.g., `adapters/mysql/`).
   - `collection`: Unified Inventory Model parsers, normalizers, direct DB metadata extractors, and offline file ingestion handlers.
   - `tools`: LangChain tools exposed safely to agents.
   - `mcp`: Model Context Protocol (MCP) server/client integrations.
   - `history`: Validation run history, diff comparison across runs, and re-validation tracking.
   - `workers`: Background job execution for document indexing and large-scale validation tasks.

3. **DBMS Isolation via `adapters/`**:
   - All DBMS-specific queries, dialect rules, catalog metadata extractors, and version semantics MUST reside under `backend/app/adapters/<dbms>/` (e.g., `backend/app/adapters/mysql/`).
   - Core services, orchestration, and APIs MUST depend on abstract adapter interfaces, never hardcoded DBMS logic.

4. **Deterministic Rule Engine vs. AI Agent Separation**:
   - **Deterministic Rule Engine (`rules/`, `validators/`)**: Responsible for parameter compatibility checks, schema/object validation, and SQL static analysis (`SQLGlot`).
   - **AI Agents (`agents/`, `orchestration/`)**: Responsible for interpreting official vendor documentation, explaining technical impact in context, generating DBA action guides, and drafting candidate SQL remediation examples & verification request documents.
   - AI Agents MUST NOT replace deterministic rule checks with probabilistic guesses.

5. **Evidence-Based Verdict Rule (No Evidence = No "PASS/NORMAL")**:
   - Every validation finding, rule evaluation, and agent recommendation MUST link to verifiable citations from official vendor documentation (`Evidence Validator`).
   - **If official documentation evidence is insufficient or missing, the system MUST NOT mark the item as normal/compatible (`PASS`)**; instead, it must flag it as `UNVERIFIED` / `INSUFFICIENT_EVIDENCE` requiring manual review.

6. **Unified Inventory Model**:
   - Both **Direct DB Connection** and **Offline File Upload** collection modes MUST normalize extracted metadata, parameters, schema definitions, stored objects, and SQL workloads into the **exact same `InventoryModel` schema** before validation begins.
   - Downstream validators, rule engines, and agents must be completely agnostic to how the inventory was collected.

7. **Safe SQL Remediation Lifecycle**:
   - Modified SQL statements generated by the AI Agent are strictly **candidate proposals** and verification artifacts.
   - The system MUST NEVER automatically execute AI-generated SQL against a target or production database.

---

## 4. Mandatory Security Principles

1. **Read-Only Target DB Access**:
   - Direct connections to target databases MUST enforce read-only sessions (`SET SESSION TRANSACTION READ ONLY` / read-only user verification) with strict connection and query timeouts.
2. **Zero Plaintext Credential Storage**:
   - Target database connection credentials (passwords, tokens, connection strings) MUST NEVER be stored in plaintext in the database, logs, history records, or error traces. Use transient memory or strong encryption (`DB_CREDENTIAL_ENCRYPTION_KEY`) only when explicitly required.
3. **PII & Sensitive Data Minimization in SQL**:
   - SQL collection and normalization pipelines MUST mask or strip literal values containing potential PII/sensitive data before storage or LLM transmission.
4. **Strict File Upload Validation**:
   - Offline file uploads MUST validate file extension allowlists, maximum byte size, MIME/content structure, character encoding, and payload integrity before parsing.
5. **Restricted Agent Execution Environment**:
   - AI Agents MUST NOT have unrestricted shell execution or arbitrary host filesystem access. Any tool access must operate within explicitly scoped, sandboxed boundaries.
6. **No Target DB Mutation in MVP**:
   - DDL/DML/parameter mutation operations against target databases are strictly prohibited and MUST NOT be implemented in the MVP.
7. **Official Vendor Domain Allowlist Only**:
   - Only documents originating from verified official vendor domains (e.g., `dev.mysql.com`, `downloads.mysql.com` for MySQL) may be ingested as authoritative rule/RAG evidence. Unofficial blogs, forums, or third-party sites MUST be rejected by the ingestion and evidence validators.

---

## 5. Development Workflow & Quality Rules

1. **Inspect Before Acting**: Always check the current workspace state before creating or modifying files.
2. **Plan Before Coding**: Document the implementation plan and explicit file list before executing each step.
3. **Strict Scope Discipline**:
   - Implement ONLY the features authorized for the current step.
   - **Do NOT pre-implement features belonging to future steps.**
4. **Verified APIs Only**:
   - Verify package APIs against current official documentation (Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2, LangGraph, LangChain, SQLGlot).
   - Never hallucinate non-existent functions, classes, or parameters.
5. **No Arbitrary Mocks**:
   - Do not build fake/mock-only implementations where real deterministic logic belongs.
   - When an external environment (such as a live target MySQL instance or external LLM API) is unavailable during automated testing, cleanly separate **Abstract Interfaces / Protocols** from **Explicit Test Fixtures** (`tests/fixtures/`).
6. **Verify and Report**:
   - Run verification checks/tests at the end of every step and report the created/modified file list along with verification results.
