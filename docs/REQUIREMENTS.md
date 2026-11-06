# Requirements Specification — DB Upgrade Impact Analysis & Validation AI Agent

## 1. Purpose & MVP Scope

- **System Name**: DB Upgrade Impact Analysis & Validation AI Agent
- **Primary Goal**: Automate and validate DBMS version upgrade impact analysis grounded strictly in official vendor documentation, deterministic static analysis, and Multi-Agent reasoning.
- **MVP Target Scope**: **MySQL 8.0 → MySQL 8.4** (LTS) upgrade impact analysis and validation.
- **Future Extensibility Scope**: Architectural interfaces prepared for MariaDB, PostgreSQL, and Oracle (excluded from MVP implementation).

---

## 2. Core Functional Requirements (FR)

### FR-01: Official Vendor Documentation Analysis
- **Description**: Ingest, chunk, index, and analyze official vendor release notes, upgrade guides, and deprecated/removed feature documentation for the source-to-target version transition (MySQL 8.0 → 8.4).
- **Capabilities**:
  - Hybrid RAG (dense vector search via `pgvector` + sparse/keyword search) with Corrective Retrieval (CRAG) relevance grading.
  - Strictly restrict document sources to official vendor domains (`dev.mysql.com`, `downloads.mysql.com`).
  - Categorize changes into System Variables/Parameters, Data Types & Schemas, Built-in Functions & Operators, Reserved Keywords, Authentication & Security, Storage Engines, and Replication/Clustering.

### FR-02: Parameter Change Impact Validation
- **Description**: Validate the target database's active and configured system variables (`SHOW GLOBAL VARIABLES` / `my.cnf` inventory) against version upgrade rules.
- **Capabilities**:
  - Deterministic **Parameter Rule Engine** detecting:
    - Removed parameters (will cause startup failure in MySQL 8.4 if present in configuration).
    - Deprecated parameters (scheduled for future removal).
    - Default value changes affecting runtime behavior or optimizer plans (e.g., `mysql_native_password`, InnoDB system variables, replication variables).
    - Value range or allowed enum changes.
  - Severity classification (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`, `INSUFFICIENT_EVIDENCE`).

### FR-03: Schema & Stored Object Compatibility Validation
- **Description**: Validate schemas, tables, columns, indexes, views, stored procedures, functions, triggers, events, and user accounts.
- **Capabilities**:
  - Deterministic **Schema Validator** checking:
    - Identifier collisions with newly added reserved keywords in MySQL 8.4.
    - Deprecated/removed data types, column attributes (`AUTO_INCREMENT` on float/double, `ZEROFILL`, etc.), and character sets/collations (`utf8mb3` vs `utf8mb4`).
    - Authentication plugin compatibility (e.g., accounts using disabled/removed authentication plugins).
    - Stored routine (`PROCEDURE`, `FUNCTION`, `TRIGGER`, `EVENT`) definition syntax and SQL mode compatibility.
    - Foreign key constraint and partitioning rule compliance.

### FR-04: Application SQL Static Analysis
- **Description**: Statically analyze collected application SQL queries (from Performance Schema digests, slow query logs, or application SQL files) for upgrade compatibility.
- **Capabilities**:
  - Deterministic AST parsing and rule inspection via **SQLGlot** (MySQL dialect).
  - Detect removed or deprecated SQL functions, operators, syntax constructs, optimizer hints, and unquoted reserved word usage.
  - Mask literal values containing potential PII/sensitive data during ingestion.

### FR-05: DBA Action Guide Generation
- **Description**: Generate actionable, structured pre-upgrade, upgrade, and post-upgrade checklists and configuration modification guides for DBAs.
- **Capabilities**:
  - Provide exact configuration changes (`my.cnf` / `SET PERSIST` examples), account migration steps, and schema preparation DDL guidelines.
  - Every recommendation must include official documentation citations and rollback considerations.

### FR-06: Application Remediated SQL Examples & Verification Request Generation
- **Description**: Generate candidate modified SQL statements for incompatible queries and produce formal Verification Request packages for application development teams.
- **Capabilities**:
  - Side-by-side comparison (`Original SQL` vs. `Candidate Remediated SQL`) rendered in the Frontend **Monaco Diff Editor**.
  - Structured Verification Request document containing: SQL ID/fingerprint, root cause of incompatibility, official doc citation, original SQL, proposed SQL, expected behavioral equivalence notes, and test checklist.
  - **Safety Constraint**: Candidate SQL is never auto-applied to any database.

### FR-07: Dual Collection Support (Direct DB Connection & Offline File Upload)
- **Description**: Support both online direct metadata collection and air-gapped offline file upload, normalizing both into a single **Unified Inventory Model**.
- **Capabilities**:
  - **Direct DB Connection**: Read-only connection to MySQL 8.0 metadata views (`information_schema`, `performance_schema`, `SHOW GLOBAL VARIABLES`) with strict timeouts and zero plaintext credential storage.
  - **Offline File Upload**: Upload pre-collected JSON/SQL/CSV diagnostic bundles with strict validation of file extensions, byte size, structure, and integrity.

### FR-08: Collection SQL Scripts & File Format Guide
- **Description**: Provide ready-to-run diagnostic SQL scripts and clear file format specifications (`collectors/`) for environments where direct DB connection is restricted by security policies.
- **Capabilities**:
  - Downloadable MySQL 8.0 read-only extraction scripts (`collectors/mysql/`).
  - Clear schema documentation and sample templates for offline upload files.

### FR-09: Validation History & Re-validation Management
- **Description**: Persist validation runs, compare historical validation snapshots, and track remediation progress across iterative re-validations.
- **Capabilities**:
  - Record validation run metadata, inventory snapshot summary, rule version, and item-level findings.
  - Compare Run $N$ vs. Run $N+1$ (Resolved issues, Remaining issues, Newly introduced issues, Unverified items).

### FR-10: Official Documentation Evidence-Grounded Verdicts
- **Description**: Enforce strict citation and evidence validation on every output.
- **Capabilities**:
  - **Evidence Validator** verifies that every finding links to an indexed official documentation chunk and URL.
  - **Mandatory Rule**: When official documentation evidence is insufficient or unavailable, the system MUST NOT judge the item as `NORMAL` / `PASS`; it must mark it as `INSUFFICIENT_EVIDENCE` requiring manual verification.

---

## 3. Non-Functional & Security Requirements (NFR)

1. **Read-Only Enforcement (SEC-01)**: Direct target DB connections must operate exclusively in read-only mode. Mutation operations against target databases are excluded from the MVP.
2. **Credential Protection (SEC-02)**: Target DB credentials must never be stored in plaintext in the database, logs, or traces.
3. **PII Minimization (SEC-03)**: SQL literals must be sanitized/masked during collection before storage or LLM processing.
4. **File Upload Hardening (SEC-04)**: Strict validation of file extension allowlist, maximum file size, JSON/CSV/SQL structure, and checksum/encoding integrity.
5. **Agent Sandboxing (SEC-05)**: Agents must operate with scoped tools only; arbitrary shell or host filesystem execution is restricted.
6. **Domain Allowlist (SEC-06)**: Only official vendor domains (`dev.mysql.com`, `downloads.mysql.com`) are accepted as rule/RAG ground truth.
7. **Deterministic Reproducibility (NFR-01)**: Given the same `InventoryModel` and rule catalog version, the Parameter Rule Engine, Schema Validator, and SQLGlot Validator must produce 100% identical deterministic findings.
8. **DBMS Extensibility (NFR-02)**: Adding a new DBMS in future releases must be achievable by implementing the `adapters/` interface and version rule catalog without refactoring core services or API schemas.
