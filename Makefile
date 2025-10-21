# HEPilot Unified Makefile
# Central control for the entire HEPilot system
# Orchestrates: arXiv adapter, embedding layer, database, testing

.PHONY: help setup clean test docs

# Default target
.DEFAULT_GOAL := help

# Configuration
PYTHON := python3
VENV := .venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip
PYTEST := $(VENV_BIN)/pytest
PYTHONPATH := $(shell pwd)

# Directories
ARXIV_ADAPTER_DIR := src/collector/adapters/arxiv
ARXIV_OUTPUT_DIR := $(ARXIV_ADAPTER_DIR)/arxiv_output
SCRIPTS_DIR := scripts
CONFIG_DIR := config
DOCS_DIR := docs

# Database
DB_NAME := hepilot
DB_USER := hep
DB_PASSWORD := hep
DB_HOST := localhost
DB_PORT := 5432
DB_URL := postgresql+asyncpg://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(DB_NAME)

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(CYAN)HEPilot - High Energy Physics Literature Orchestration Tool$(NC)"
	@echo ""
	@echo "$(GREEN)Usage:$(NC) make [target]"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-25s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(GREEN)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup & Installation

setup: setup-venv install-deps setup-db ## Complete setup (venv + deps + database)

setup-venv: ## Create Python virtual environment
	@echo "$(CYAN)Creating virtual environment...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
		echo "$(GREEN)✓ Virtual environment created$(NC)"; \
	else \
		echo "$(YELLOW)Virtual environment already exists$(NC)"; \
	fi

install-deps: setup-venv ## Install all dependencies
	@echo "$(CYAN)Installing dependencies...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@$(PIP) install -r requirements-embedding.txt
	@$(PIP) install -r requirements-dev.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

setup-db: ## Setup PostgreSQL database and run migrations
	@echo "$(CYAN)Setting up database...$(NC)"
	@echo "  Creating database '$(DB_NAME)' if not exists..."
	@psql -U postgres -h $(DB_HOST) -p $(DB_PORT) -tc "SELECT 1 FROM pg_database WHERE datname = '$(DB_NAME)'" | grep -q 1 || \
		psql -U postgres -h $(DB_HOST) -p $(DB_PORT) -c "CREATE DATABASE $(DB_NAME) OWNER $(DB_USER);" 2>/dev/null || true
	@echo "  Running migrations..."
	@cd src/embedding && PYTHONPATH=$(PYTHONPATH) $(VENV_BIN)/alembic upgrade head
	@echo "$(GREEN)✓ Database setup complete$(NC)"

##@ ArXiv Adapter

arxiv-dev: ## Run arXiv adapter in development mode (5 papers)
	@echo "$(CYAN)Running arXiv adapter (development mode)...$(NC)"
	@cd $(ARXIV_ADAPTER_DIR) && ./run.sh dev

arxiv-prod: ## Run arXiv adapter in production mode
	@echo "$(CYAN)Running arXiv adapter (production mode)...$(NC)"
	@cd $(ARXIV_ADAPTER_DIR) && ./run.sh prod

arxiv-download: ## Download papers only (no processing)
	@echo "$(CYAN)Downloading papers...$(NC)"
	@cd $(ARXIV_ADAPTER_DIR) && ./run.sh download

arxiv-process: ## Process already downloaded PDFs
	@echo "$(CYAN)Processing downloaded papers...$(NC)"
	@cd $(ARXIV_ADAPTER_DIR) && ./run.sh process

arxiv-clean: ## Clean arXiv adapter outputs
	@echo "$(CYAN)Cleaning arXiv adapter outputs...$(NC)"
	@cd $(ARXIV_ADAPTER_DIR) && make clean
	@echo "$(GREEN)✓ ArXiv outputs cleaned$(NC)"

##@ Embedding Layer

embed-ingest: ## Ingest arXiv outputs into embedding layer
	@echo "$(CYAN)Ingesting chunks into embedding layer...$(NC)"
	@if [ ! -d "$(ARXIV_OUTPUT_DIR)" ]; then \
		echo "$(RED)✗ ArXiv output directory not found$(NC)"; \
		echo "$(YELLOW)  Run 'make arxiv-dev' or 'make arxiv-prod' first$(NC)"; \
		exit 1; \
	fi
	@PYTHONPATH=$(PYTHONPATH) $(VENV_BIN)/python $(SCRIPTS_DIR)/ingest_embeddings.py \
		--input $(ARXIV_OUTPUT_DIR) \
		--config $(CONFIG_DIR)/embedding.toml
	@echo "$(GREEN)✓ Ingestion complete$(NC)"

embed-ingest-dry: ## Dry run of embedding ingestion (parse only)
	@echo "$(CYAN)Dry run: Parsing chunk files...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(VENV_BIN)/python $(SCRIPTS_DIR)/ingest_embeddings.py \
		--input $(ARXIV_OUTPUT_DIR) \
		--config $(CONFIG_DIR)/embedding.toml \
		--dry-run

embed-migrate: ## Run embedding layer database migrations
	@echo "$(CYAN)Running embedding migrations...$(NC)"
	@cd src/embedding && PYTHONPATH=$(PYTHONPATH) $(VENV_BIN)/alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete$(NC)"

embed-migrate-down: ## Rollback embedding migrations
	@echo "$(CYAN)Rolling back migrations...$(NC)"
	@cd src/embedding && PYTHONPATH=$(PYTHONPATH) $(VENV_BIN)/alembic downgrade -1

embed-migrate-reset: ## Reset database (downgrade to base)
	@echo "$(YELLOW)⚠️  This will DROP all embedding tables!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		cd src/embedding && PYTHONPATH=$(PYTHONPATH) $(VENV_BIN)/alembic downgrade base; \
		echo "$(GREEN)✓ Database reset$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

embed-status: ## Show embedding layer status
	@echo "$(CYAN)Embedding Layer Status:$(NC)"
	@echo ""
	@echo "Database:"
	@cd src/embedding && PYTHONPATH=$(PYTHONPATH) $(VENV_BIN)/alembic current
	@echo ""
	@echo "Components:"
	@echo "  DocStore:  PostgreSQL ($(DB_URL))"
	@echo "  VectorDB:  ChromaDB (.data/chroma)"
	@echo "  Encoder:   BGE-base-en-v1.5"

##@ Complete Workflows

pipeline-dev: arxiv-dev embed-ingest ## Complete development pipeline (5 papers)
	@echo ""
	@echo "$(GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "$(GREEN)✨ Development pipeline complete!$(NC)"
	@echo "$(GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"

pipeline-prod: arxiv-prod embed-ingest ## Complete production pipeline
	@echo ""
	@echo "$(GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "$(GREEN)✨ Production pipeline complete!$(NC)"
	@echo "$(GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"

pipeline-status: ## Show status of entire pipeline
	@echo "$(CYAN)HEPilot Pipeline Status$(NC)"
	@echo ""
	@echo "$(CYAN)1. ArXiv Adapter:$(NC)"
	@if [ -d "$(ARXIV_OUTPUT_DIR)" ]; then \
		file_count=$$(find $(ARXIV_OUTPUT_DIR) -name "*chunk_output.json" 2>/dev/null | wc -l); \
		echo "  $(GREEN)✓$(NC) Output directory exists"; \
		echo "  $(GREEN)✓$(NC) $$file_count chunk files found"; \
	else \
		echo "  $(RED)✗$(NC) No output directory (run 'make arxiv-dev')"; \
	fi
	@echo ""
	@echo "$(CYAN)2. Embedding Layer:$(NC)"
	@make embed-status 2>/dev/null || echo "  $(RED)✗$(NC) Database not set up"

##@ Testing

test: ## Run all tests
	@echo "$(CYAN)Running all tests...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(PYTEST) tests/ -v

test-embedding: ## Run embedding layer tests only
	@echo "$(CYAN)Running embedding layer tests...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(PYTEST) tests/unit/embedding/ -v

test-collector: ## Run collector tests only
	@echo "$(CYAN)Running collector tests...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(PYTEST) tests/unit/collector/ -v -k collector 2>/dev/null || \
		echo "$(YELLOW)No collector tests found$(NC)"

test-cov: ## Run tests with coverage report
	@echo "$(CYAN)Running tests with coverage...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(PYTEST) tests/ -v --cov=src --cov-report=html --cov-report=term

test-watch: ## Run tests in watch mode
	@echo "$(CYAN)Running tests in watch mode...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(PYTEST) tests/ -v --looponfail

##@ Local Development (No PostgreSQL Required)

local-test-pipeline: ## Test complete pipeline locally (no PostgreSQL needed)
	@echo "$(CYAN)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║  HEPilot Local Pipeline Test (No External Services)       ║$(NC)"
	@echo "$(CYAN)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)This will:$(NC)"
	@echo "  1. Download 5 arXiv papers"
	@echo "  2. Process and chunk them"
	@echo "  3. Generate embeddings"
	@echo "  4. Store vectors in ChromaDB (local)"
	@echo "  5. Test retrieval"
	@echo ""
	@echo "$(GREEN)Starting pipeline...$(NC)"
	@echo ""
	@echo "$(CYAN)═══ Step 1: ArXiv Adapter ═══$(NC)"
	@cd $(ARXIV_ADAPTER_DIR) && ./run.sh dev
	@echo ""
	@echo "$(CYAN)═══ Step 2: Embedding Pipeline ═══$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(VENV_BIN)/python $(SCRIPTS_DIR)/test_local_pipeline.py \
		--input $(ARXIV_OUTPUT_DIR) \
		--config $(CONFIG_DIR)/embedding-local.toml
	@echo ""
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  ✅ Local pipeline test complete!                          ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════╝$(NC)"

local-test-embed-only: ## Test embedding layer only (assumes chunks exist)
	@echo "$(CYAN)Testing embedding layer with existing chunks...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(VENV_BIN)/python $(SCRIPTS_DIR)/test_local_pipeline.py \
		--input $(ARXIV_OUTPUT_DIR) \
		--config $(CONFIG_DIR)/embedding-local.toml

local-clean: ## Clean local data (ChromaDB, cache, chunks)
	@echo "$(CYAN)Cleaning local data...$(NC)"
	@rm -rf .data/chroma
	@rm -rf .cache/models
	@rm -rf $(ARXIV_OUTPUT_DIR)
	@echo "$(GREEN)✓ Local data cleaned$(NC)"

local-status: ## Show local pipeline status
	@echo "$(CYAN)Local Pipeline Status$(NC)"
	@echo ""
	@echo "$(CYAN)ArXiv Chunks:$(NC)"
	@if [ -d "$(ARXIV_OUTPUT_DIR)" ]; then \
		file_count=$$(find $(ARXIV_OUTPUT_DIR) -name "*chunk_output.json" 2>/dev/null | wc -l); \
		echo "  ✓ Output directory exists"; \
		echo "  ✓ $$file_count chunk files"; \
	else \
		echo "  ✗ No output directory"; \
	fi
	@echo ""
	@echo "$(CYAN)ChromaDB:$(NC)"
	@if [ -d ".data/chroma" ]; then \
		echo "  ✓ Vector database exists"; \
	else \
		echo "  ✗ No vector database (run local-test-pipeline)"; \
	fi
	@echo ""
	@echo "$(CYAN)Model Cache:$(NC)"
	@if [ -d ".cache/models" ]; then \
		echo "  ✓ Models cached"; \
	else \
		echo "  ✗ No cached models (will download on first run)"; \
	fi

##@ Database Management

db-shell: ## Open PostgreSQL shell
	@psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d $(DB_NAME)

db-reset: ## Drop and recreate database (WARNING: deletes all data)
	@echo "$(RED)⚠️  WARNING: This will DELETE ALL DATA!$(NC)"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "$(CYAN)Dropping database...$(NC)"; \
		psql -U postgres -h $(DB_HOST) -p $(DB_PORT) -c "DROP DATABASE IF EXISTS $(DB_NAME);"; \
		psql -U postgres -h $(DB_HOST) -p $(DB_PORT) -c "CREATE DATABASE $(DB_NAME) OWNER $(DB_USER);"; \
		echo "$(CYAN)Running migrations...$(NC)"; \
		make embed-migrate; \
		echo "$(GREEN)✓ Database reset complete$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

db-backup: ## Backup database to file
	@echo "$(CYAN)Backing up database...$(NC)"
	@mkdir -p backups
	@pg_dump -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d $(DB_NAME) > backups/hepilot_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Backup created in backups/$(NC)"

db-restore: ## Restore database from latest backup
	@echo "$(CYAN)Restoring from latest backup...$(NC)"
	@latest=$$(ls -t backups/*.sql 2>/dev/null | head -1); \
	if [ -z "$$latest" ]; then \
		echo "$(RED)✗ No backup files found$(NC)"; \
		exit 1; \
	fi; \
	echo "$(YELLOW)Restoring from: $$latest$(NC)"; \
	psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d $(DB_NAME) < $$latest; \
	echo "$(GREEN)✓ Restore complete$(NC)"

##@ Cleanup

clean: arxiv-clean ## Clean all generated files
	@echo "$(CYAN)Cleaning generated files...$(NC)"
	@rm -rf .pytest_cache
	@rm -rf .coverage htmlcov
	@rm -rf __pycache__ */__pycache__ */*/__pycache__
	@rm -rf *.egg-info
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-data: ## Clean all data (vectors, cache, outputs)
	@echo "$(YELLOW)⚠️  This will delete all processed data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf .data; \
		rm -rf .cache; \
		rm -rf $(ARXIV_OUTPUT_DIR); \
		echo "$(GREEN)✓ Data cleaned$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

clean-venv: ## Remove virtual environment
	@echo "$(CYAN)Removing virtual environment...$(NC)"
	@rm -rf $(VENV)
	@echo "$(GREEN)✓ Virtual environment removed$(NC)"

clean-all: clean clean-data ## Clean everything except venv
	@echo "$(GREEN)✓ All cleaned$(NC)"

nuke: clean-all clean-venv db-reset ## Nuclear option: delete everything and reset
	@echo "$(GREEN)✓ System reset to clean state$(NC)"

##@ Development

lint: ## Run linters
	@echo "$(CYAN)Running linters...$(NC)"
	@$(VENV_BIN)/ruff check src/ tests/ || true
	@$(VENV_BIN)/mypy src/ || true

format: ## Format code
	@echo "$(CYAN)Formatting code...$(NC)"
	@$(VENV_BIN)/black src/ tests/
	@$(VENV_BIN)/isort src/ tests/

format-check: ## Check code formatting
	@echo "$(CYAN)Checking code formatting...$(NC)"
	@$(VENV_BIN)/black --check src/ tests/
	@$(VENV_BIN)/isort --check src/ tests/

##@ Documentation

docs: ## Generate documentation
	@echo "$(CYAN)Generating documentation...$(NC)"
	@echo "$(YELLOW)Documentation generation not yet implemented$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(CYAN)Serving documentation...$(NC)"
	@echo "$(YELLOW)Documentation serving not yet implemented$(NC)"

##@ Monitoring

health: ## Check health of all components
	@echo "$(CYAN)Checking component health...$(NC)"
	@echo ""
	@echo "$(CYAN)Database:$(NC)"
	@psql -U $(DB_USER) -h $(DB_HOST) -p $(DB_PORT) -d $(DB_NAME) -c "SELECT 1;" > /dev/null 2>&1 && \
		echo "  $(GREEN)✓$(NC) PostgreSQL connected" || \
		echo "  $(RED)✗$(NC) PostgreSQL connection failed"
	@echo ""
	@echo "$(CYAN)Vector Store:$(NC)"
	@if [ -d ".data/chroma" ]; then \
		echo "  $(GREEN)✓$(NC) ChromaDB directory exists"; \
	else \
		echo "  $(YELLOW)⚠$(NC)  ChromaDB not initialized"; \
	fi
	@echo ""
	@echo "$(CYAN)Python Environment:$(NC)"
	@if [ -d "$(VENV)" ]; then \
		echo "  $(GREEN)✓$(NC) Virtual environment exists"; \
		$(VENV_BIN)/python --version; \
	else \
		echo "  $(RED)✗$(NC) Virtual environment not found"; \
	fi

logs: ## Show recent logs (if any)
	@echo "$(CYAN)Recent logs:$(NC)"
	@echo "$(YELLOW)Logging not yet implemented$(NC)"

##@ Quick Start

quickstart: setup arxiv-dev embed-ingest ## Quick start: setup + run dev pipeline
	@echo ""
	@echo "$(GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "$(GREEN)✨ Quick start complete!$(NC)"
	@echo ""
	@echo "$(CYAN)Next steps:$(NC)"
	@echo "  • Run queries: python scripts/query_example.py"
	@echo "  • Check status: make pipeline-status"
	@echo "  • Run tests: make test-embedding"
	@echo "$(GREEN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
