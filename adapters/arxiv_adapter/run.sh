#!/bin/bash

##
## ArXiv Adapter Control Script
##
## Usage:
##   ./run.sh dev    - Development mode (5 papers)
##   ./run.sh prod   - Production mode (All papers)
##

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MODE="${1:-dev}"

echo "=========================================="
echo "HEPilot ArXiv Adapter"
echo "=========================================="
echo "Mode: $MODE"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "WARNING: jq not found (optional, for JSON validation)"
fi

if [ ! -f "adapter_config.json" ]; then
    echo "ERROR: adapter_config.json not found"
    exit 1
fi

echo "Validating configuration..."
python3 -c "import json; json.load(open('adapter_config.json'))" || {
    echo "ERROR: Invalid JSON in adapter_config.json"
    exit 1
}

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "Using uv (fast Python package manager)..."
    
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment with uv..."
        uv venv .venv
    fi
    
    echo "Activating virtual environment..."
    source .venv/bin/activate
    
    echo "Installing/updating dependencies with uv..."
    uv pip install -r requirements.txt
else
    echo "Using pip (uv not found, install with: pip install uv)..."
    
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    echo "Activating virtual environment..."
    source .venv/bin/activate
    
    echo "Installing/updating dependencies..."
    pip install -q -U pip
    pip install -q -r requirements.txt
fi

echo ""
echo "=========================================="
echo "Starting pipeline..."
echo "=========================================="
echo ""

if [ "$MODE" = "dev" ]; then
    echo "Running in DEVELOPMENT mode (5 papers max)"
    python3 main.py \
        --config adapter_config.json \
        --output arxiv_output \
        --query "all:lhcb" \
        --dev
elif [ "$MODE" = "prod" ]; then
    echo "Running in PRODUCTION mode (All papers)"
    python3 main.py \
        --config adapter_config.json \
        --output arxiv_output \
        --query "all:lhcb"
else
    echo "ERROR: Invalid mode '$MODE'. Use 'dev' or 'prod'"
    exit 1
fi

EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "Pipeline completed successfully!"
    echo ""
    echo "Output structure:"
    echo "  output/"
    echo "  ├── documents/"
    echo "  │   └── arxiv_{document_id}/"
    echo "  │       ├── chunks/"
    echo "  │       │   ├── chunk_NNNN.md"
    echo "  │       │   └── chunk_NNNN_metadata.json"
    echo "  │       ├── full_document.md"
    echo "  │       ├── document_metadata.json"
    echo "  │       └── processing_metadata.json"
    echo "  ├── catalog.json"
    echo "  ├── discovery_output.json"
    echo "  ├── acquisition_output.json"
    echo "  └── processing_log.json"
    echo ""
    
    if [ -f "arxiv_output/catalog.json" ]; then
        DOC_COUNT=$(python3 -c "import json; print(json.load(open('arxiv_output/catalog.json'))['document_count'])" 2>/dev/null || echo "unknown")
        echo "Documents processed: $DOC_COUNT"
    fi
    
    if [ -f "arxiv_output/processing_log.json" ]; then
        ERROR_COUNT=$(python3 -c "import json; logs=json.load(open('arxiv_output/processing_log.json')); print(sum(1 for e in logs if e['level']=='ERROR'))" 2>/dev/null || echo "unknown")
        echo "Errors encountered: $ERROR_COUNT"
    fi
else
    echo "Pipeline failed with exit code $EXIT_CODE"
    echo ""
    echo "Check arxiv_output/processing_log.json for details"
fi
echo "=========================================="

exit $EXIT_CODE
