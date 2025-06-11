# HEPilot — Comprehensive Implementation Guide

*Version 0.1 — 11 Jun 2025*

---

## Table of Contents

1. [Purpose & Scope](#1-purpose--scope)
2. [System Architecture](#2-system-architecture)
3. [Repository Layout](#3-repository-layout)
4. [Layer Specifications](#4-layer-specifications)

    4.1 [Source Collector](#41-source-collector)
   
    4.2 [Embedding Engine](#42-embedding-engine)
   
    4.3 [API Layer](#43-api-layer)
   
    4.4 [User Interface](#44-user-interface)
   
6. [Storage Design](#5-storage-design)
7. [Configuration Reference](#6-configuration-reference)
8. [CI / CD Pipeline](#7-ci--cd-pipeline)
9. [Deployment Topologies](#8-deployment-topologies)

    8.1 [Local Development](#81-local-development)

    8.2 [CERN On-Prem (plan)](#82-cern-on-prem-plan)

10. [License](#9-license)
11. [Glossary](#10-glossary)

---

## 1 · Purpose & Scope

HEPilot is a modular Retrieval-Augmented Generation (RAG) framework for High-Energy-Physics documentation. The design goals are:

* **Adapter-based** components—scrapers, embedding models, and vector stores can be swapped via config.
* **OpenAI-compatible** REST façade to support OpenAI, Ollama, LM-Studio, or any future provider.
* **Ready-made web UI** (Chatbot-UI fork) streaming answers with inline citations.
* **Full traceability**—every stored vector maps back to a verbatim text chunk.

---

## 2 · System Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      User Interface (UI)                  │
│           Chatbot-UI → /v1/chat | /rag/search             │
└──────────────┬────────────────────────────────────────────┘
               │  REST + SSE (OpenAI spec)                  
┌──────────────┴────────────────────────────────────────────┐
│                        API Layer                          │
│ FastAPI · Auth · Throttling · Metrics · Health Probes     │
└──────────────┬────────────────────────────────────────────┘
     ingest    │                                             retrieve
┌──────────────┴──────────────┐      ┌────────────────────────┴──────────────┐
│        Source Collector      │      │            Embedding Engine           │
│ scrape → clean → chunk → DB  │      │ encode → upsert/query → decode ↩text │
└──────────────────────────────┘      └───────────────────────────────────────┘
```

---

## 3 · Repository Layout

```
hepilot/
├─ src/
│  ├─ collector/
│  │   ├─ ports.py
│  │   ├─ adapters/
│  │   └─ registry.py
│  ├─ embedding/
│  │   ├─ ports.py
│  │   ├─ adapters/
│  │   └─ registry.py
│  └─ api/
│      ├─ main.py
│      ├─ routes_chat.py
│      ├─ routes_embed.py
│      ├─ routes_rag.py
│      ├─ routes_admin.py
│      └─ llm_backends/
├─ ui/                        # Chatbot-UI submodule + patches
│  └─ patches/
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  └─ contracts/
├─ docker/
│  ├─ dev.compose.yaml
│  └─ api.Dockerfile
├─ scripts/
│  └─ bootstrap.sh
├─ alembic/
├─ pyproject.toml
└─ docs/
    ├─ reference.md
    └─ adr/
```

---

## 4 · Layer Specifications

### 4.1 Source Collector

| Component    | Responsibility                        | Protocol                     |
| ------------ | ------------------------------------- | ---------------------------- |
| **Scraper**  | Fetch raw bytes + metadata from a URL | `async fetch(url) -> RawDoc` |
| **Cleaner**  | Convert raw content to plain text     | `clean(raw) -> str`          |
| **Chunker**  | Split text into token-aware windows   | `split(text) -> list[Chunk]` |
| **DocStore** | Persist chunks & metadata             | `add(chunks)` · `get(id)`    |

`RawDoc` and `Chunk` data-classes ensure common formatting.
Default adapters: `TwikiScraper`, `IndicoScraper`, `BoilerCleaner`, `RecursiveSplitter`, `PostgresDocStore`.

### 4.2 Embedding Engine

| Component    | Responsibility                     | Protocol                          |
| ------------ | ---------------------------------- | --------------------------------- |
| **Encoder**  | Text → vector                      | `async embed(texts) -> ndarray`   |
| **VectorDB** | Vector storage & similarity search | `upsert(id,vec)` · `query(vec,k)` |
| **Decoder**  | Vector-ID → plain chunk            | `lookup(id) -> Chunk`             |

Default adapters: `ONNXBGEEncoder`, `ChromaDB`, `PGDecoder`.
Decoder retrieves text from `doc_segments` and **not** from vector-DB payloads, guaranteeing traceability.

### 4.3 API Layer

*Entry*: `uvicorn hepilot.api.main:app`.

| Route                       | Contract    | Notes                       |
| --------------------------- | ----------- | --------------------------- |
| `POST /v1/chat/completions` | OpenAI v1.7 | Streams when `stream=true`  |
| `POST /v1/embeddings`       | OpenAI v1.7 | Calls Encoder               |
| `POST /rag/search`          | Custom      | `{query,k}` → ranked chunks |
| `GET /healthz`              | 200 JSON    | Liveness                    |
| `GET /metrics`              | Prometheus  | Instrumented                |

Back-end drivers (`openai`, `ollama`, `lmstudio`) implement a common `ChatBackend` protocol.

### 4.4 User Interface

* Git submodule: `ui/chatbot-ui`
* Patches add an RAG side-panel and branding.
* Build: `pnpm build && pnpm export` → static files served at `/ui/`.

---

## 5 · Storage Design

### 5.1 PostgreSQL — `doc_segments`

| column       | type          | constraints        |
| ------------ | ------------- | ------------------ |
| `id`         | `uuid`        | PK                 |
| `doc_id`     | `uuid`        | FK `documents(id)` |
| `text`       | `text`        | plain chunk        |
| `meta`       | `jsonb`       | scraper, url, etc. |
| `created_at` | `timestamptz` | `now()`            |

`pg_trgm` index on `text` improves fuzzy lookup.

### 5.2 Vector Store

*Default*: Chroma collection `hepilot`
Vectors reference `doc_segments.id`; payloads are intentionally empty.

---

## 6 · Configuration Reference

| Variable          | Default                               | Description                |
| ----------------- | ------------------------------------- | -------------------------- |
| `HP_CONFIG`       | `config.toml`                         | Bootstrap file             |
| `DB_DSN`          | `postgresql+asyncpg://hep:hep@db/hep` | Database DSN               |
| `HP_BACKEND`      | `openai`                              | LLM backend                |
| `OPENAI_API_KEY`  | —                                     | Required if backend=openai |
| `OLLAMA_BASE_URL` | `http://ollama:11434`                 | if backend=ollama          |
| `ENCODER_IMPL`    | `onnx_bge`                            | Encoder adapter            |
| `VDB_IMPL`        | `chroma`                              | Vector DB adapter          |
| `SCRAPER_IMPL`    | `twiki`                               | Scraper adapter            |
| `LOG_LEVEL`       | `INFO`                                | JSON logs                  |

---

## 7 · CI / CD Pipeline

| Stage                 | Task                                             |
| --------------------- | ------------------------------------------------ |
| **Lint**              | `ruff check --fix` + `mypy --strict`             |
| **Unit Tests**        | `pytest -m "not integration and not contract"`   |
| **Build**             | Docker image `ghcr.io/melashri/hepilot-api:$SHA` |
| **Integration Tests** | `docker compose up` + integration suite          |
| **Contract Tests**    | Verify OpenAI-spec parity                        |
| **Publish**           | PyPI wheel & container on `main` branch          |

---

## 8 · Deployment Topologies

### 8.1 Local Development

`docker/dev.compose.yaml` provisions:

* PostgreSQL 15
* Chroma
* API (auto-reload)
* Optional Ollama

### 8.2 CERN On-Prem (plan)

A provisional approach, subject to infrastructure constraints:

1. **Container Runtime**

   * Convert the `hepilot-api` OCI image to Singularity (`sif`) so it can run on lxplus and batch queues without root privileges.
   * Store images on EOS or CVMFS for fast distribution.

2. **Orchestrator Options**

   * **OpenShift/OKD** clusters already used by LHCb Online could host long-running API pods.
   * For small-scale deployments, systemd-managed Singularity instances behind Apache reverse proxy suffice.

3. **Networking & Auth**

   * Expose API behind CERN Single Sign-On (Keycloak/OIDC) using mod\_auth\_openidc.
   * Use internal FQDN (`hepilot.web.cern.ch`) with CERN TLS certificates issued by IT-CA.

4. **Storage**

   * PostgreSQL instance on central DB service (DBOD) or a local Postgres pod with persistent volumes on CephFS.
   * Vector store: Chroma backed by CephFS or switch to Qdrant if an existing deployment exists.

5. **Observability**

   * Enable OpenTelemetry tracing. Point OTLP exporter at CERN Jaeger/Tempo.
   * Push Prometheus metrics to the central Prometheus federation via node-exporter side-car.

6. **Batch Ingestion**

   * Run ingestion jobs as HTCondor batch submissions; they mount `/cvmfs` and write directly to Postgres and VectorDB over the CERN network.

Each item requires validation with CERN IT policies before finalisation.

---



## 9 · Glossary

| Term            | Meaning                                               |
| --------------- | ----------------------------------------------------- |
| **RAG**         | Retrieval-Augmented Generation                        |
| **Chunk**       | Fixed-size text window fed to the encoder             |
| **Vector DB**   | Database optimised for nearest-neighbour search       |
| **OpenAI spec** | HTTP/JSON contract used by api.openai.com             |
| **Entry-point** | Python packaging hook for plugin discovery            |
| **Adapter**     | Concrete implementation of a port interface           |
| **Port**        | Abstract Python protocol defining callable signatures |
| **DocStore**    | Persistence layer for plain-language chunks           |
| **SSE**         | Server-Sent Events (HTTP streaming)                   |

