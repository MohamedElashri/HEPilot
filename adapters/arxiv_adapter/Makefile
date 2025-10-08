# HEPilot ArXiv Adapter Makefile
# Alternative interface for common tasks (complements run.sh)

.PHONY: help dev prod clean clean-cache clean-venv clean-all clean-full quick-clean reset nuke

# Default target
.DEFAULT_GOAL := help

# Configuration
PYTHON := python3
VENV := .venv
OUTPUT_DIR := arxiv_output
CACHE_DIR := .model_cache
DOWNLOADS_DIR := $(OUTPUT_DIR)/downloads

##@ General

help: ## Display this help message
	@echo "HEPilot ArXiv Adapter - Makefile"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  %-20s %s\n", $$1, $$2 } /^##@/ { printf "\n%s\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Execution

dev: ## Run pipeline in development mode (5 papers)
	@echo "Running in development mode via run.sh..."
	@./run.sh dev

prod: ## Run pipeline in production mode
	@echo "Running in production mode via run.sh..."
	@./run.sh prod

##@ Cleanup

clean: ## Remove output files (keeps model cache)
	@echo "Cleaning output directory..."
	@if [ -d "$(OUTPUT_DIR)" ]; then \
		echo "  Removing $(OUTPUT_DIR)/"; \
		rm -rf $(OUTPUT_DIR); \
		echo "  ✓ Output directory cleaned"; \
	else \
		echo "  Output directory not found (already clean)"; \
	fi

clean-cache: ## Remove model cache files
	@echo "Cleaning model cache..."
	@if [ -d "$(CACHE_DIR)" ]; then \
		echo "  Removing $(CACHE_DIR)/"; \
		rm -rf $(CACHE_DIR); \
		echo "  ✓ Model cache cleaned"; \
	else \
		echo "  Model cache not found (already clean)"; \
	fi

clean-venv: ## Remove virtual environment
	@echo "Cleaning virtual environment..."
	@if [ -d "$(VENV)" ]; then \
		echo "  Removing $(VENV)/"; \
		rm -rf $(VENV); \
		echo "  ✓ Virtual environment cleaned"; \
	else \
		echo "  Virtual environment not found (already clean)"; \
	fi

clean-all: clean clean-cache ## Remove all generated files (output + cache)
	@echo ""
	@echo "All generated files cleaned!"

clean-full: clean-all clean-venv ## Remove everything including virtual environment
	@echo ""
	@echo "⚠️  Complete cleanup done. Run './run.sh dev' to start fresh."

##@ Quick Actions

quick-clean: clean ## Quick clean (alias for clean)
	@echo ""
	@echo "Quick clean complete! Ready for next run."

reset: clean-all ## Reset to fresh state (keeps venv)
	@echo ""
	@echo "Reset complete! Ready for fresh run."

nuke: clean-full ## Nuclear option - remove EVERYTHING
	@echo ""
	@echo "⚠️  Nuclear cleanup done. Run './run.sh dev' to start fresh."
