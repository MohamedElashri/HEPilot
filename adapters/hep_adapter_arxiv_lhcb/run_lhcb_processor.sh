#!/bin/bash

# run_lhcb_processor.sh
# Automated LHCb ArXiv paper processing script for HEPilot
# This script automates the processing of all LHCb papers from ArXiv
# with comprehensive LaTeX support and content filtering for RAG applications.
# It handles logging, error recovery, and incremental updates.
# Author: HEPilot System
# Version: 2.0.0
# Date: 2025-09-14

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_DIR="${SCRIPT_DIR}/logs"
readonly TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
readonly LOG_FILE="${LOG_DIR}/lhcb_processing_${TIMESTAMP}.log"
readonly ERROR_LOG="${LOG_DIR}/lhcb_errors_${TIMESTAMP}.log"
readonly PID_FILE="${SCRIPT_DIR}/.lhcb_processor.pid"
# Processing configuration
readonly MAX_RETRIES=3
readonly RETRY_DELAY=30
readonly HEALTH_CHECK_INTERVAL=300  # 5 minutes
readonly UPDATE_INTERVAL=3600       # 1 hour
readonly BACKUP_INTERVAL=86400      # 24 hours

# Virtual environment detection (can be overridden with VENV_PATH environment variable)
VENV_PATH="${VENV_PATH:-}"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Function declarations

# Print colored log message with timestamp
# Args: level (INFO, WARN, ERROR), message
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local color=""
    
    case "$level" in
        "INFO")  color="$GREEN" ;;
        "WARN")  color="$YELLOW" ;;
        "ERROR") color="$RED" ;;
        "DEBUG") color="$BLUE" ;;
    esac
    
    # Create log directory if it doesn't exist
    mkdir -p "$LOG_DIR"
    
    echo -e "${color}[${timestamp}] ${level}: ${message}${NC}" | tee -a "$LOG_FILE"
}

# Check if virtual environment exists and activate it
# Returns: 0 if successful, 1 if failed
setup_environment() {
    log_message "INFO" "Setting up Python virtual environment"
    
    # Auto-detect virtual environment if not specified
    if [[ -z "$VENV_PATH" ]]; then
        local possible_venvs=(
            "${SCRIPT_DIR}/../../.venv"
            "${SCRIPT_DIR}/../.venv"
            "${SCRIPT_DIR}/.venv"
            "${SCRIPT_DIR}/../../venv"
            "${SCRIPT_DIR}/../venv"
            "${SCRIPT_DIR}/venv"
            "${SCRIPT_DIR}/../../env"
            "${SCRIPT_DIR}/../env"
            "${SCRIPT_DIR}/env"
        )
        
        for venv_path in "${possible_venvs[@]}"; do
            if [[ -d "$venv_path" && -f "$venv_path/bin/activate" ]]; then
                VENV_PATH="$venv_path"
                log_message "INFO" "Auto-detected virtual environment at: $VENV_PATH"
                break
            fi
        done
        
        if [[ -z "$VENV_PATH" ]]; then
            log_message "ERROR" "No virtual environment found. Please create one or set VENV_PATH environment variable."
            log_message "ERROR" "Example: python -m venv .venv && source .venv/bin/activate"
            return 1
        fi
    fi
    
    # Check if virtual environment exists
    if [[ ! -d "$VENV_PATH" ]]; then
        log_message "ERROR" "Virtual environment not found at $VENV_PATH"
        return 1
    fi
    
    if [[ ! -f "$VENV_PATH/bin/activate" ]]; then
        log_message "ERROR" "Virtual environment activation script not found at $VENV_PATH/bin/activate"
        return 1
    fi
    
    # Activate virtual environment
    # shellcheck source=/dev/null
    source "$VENV_PATH/bin/activate"
    log_message "INFO" "Virtual environment activated: $VENV_PATH"
    
    # Verify we're in the virtual environment
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        log_message "ERROR" "Failed to activate virtual environment"
        return 1
    fi
    
    # Verify required packages and install if missing
    if ! python -c "import docling, arxiv" 2>/dev/null; then
        log_message "WARN" "Installing missing dependencies in virtual environment"
        
        # Check if pip is available, if not try to install it
        if ! python -c "import pip" 2>/dev/null; then
            log_message "INFO" "pip not found, installing pip using ensurepip"
            python -m ensurepip --upgrade 2>&1 | tee -a "$LOG_FILE"
            
            # If ensurepip fails, try alternative methods
            if ! python -c "import pip" 2>/dev/null; then
                log_message "WARN" "ensurepip failed, trying alternative pip installation"
                # Try downloading get-pip.py
                curl -sS https://bootstrap.pypa.io/get-pip.py | python - 2>&1 | tee -a "$LOG_FILE"
                
                if ! python -c "import pip" 2>/dev/null; then
                    log_message "ERROR" "Failed to install pip in virtual environment"
                    log_message "ERROR" "Please recreate the virtual environment: python -m venv --clear $VENV_PATH"
                    return 1
                fi
            fi
        fi
        
        # Ensure we're using pip from the virtual environment
        python -m pip install --upgrade pip 2>&1 | tee -a "$LOG_FILE"
        python -m pip install docling arxiv requests 2>&1 | tee -a "$LOG_FILE"
        
        # Verify installation
        if ! python -c "import docling, arxiv" 2>/dev/null; then
            log_message "ERROR" "Failed to install required packages"
            return 1
        fi
        
        log_message "INFO" "Dependencies installed successfully"
    else
        log_message "INFO" "All required packages are available"
    fi
    
    return 0
}

# Create necessary directories and files
initialize_directories() {
    log_message "INFO" "Initializing directories"
    
    mkdir -p "$LOG_DIR"
    mkdir -p "${SCRIPT_DIR}/hepilot_output"
    mkdir -p "${SCRIPT_DIR}/hepilot_output/cache"
    mkdir -p "${SCRIPT_DIR}/hepilot_output/backup"
    
    # Create state file if it doesn't exist
    local state_file="${SCRIPT_DIR}/hepilot_output/state.json"
    if [[ ! -f "$state_file" ]]; then
        echo '{"last_run": null, "processed_count": 0, "last_arxiv_id": null}' > "$state_file"
        log_message "INFO" "Created initial state file"
    fi
}

# Check system resources and prerequisites
# Returns: 0 if system is ready, 1 if not
check_system_health() {
    log_message "INFO" "Performing system health check"
    
    # Check disk space (require at least 10GB free)
    local free_space_kb
    free_space_kb=$(df "$SCRIPT_DIR" | awk 'NR==2 {print $4}')
    local free_space_gb=$((free_space_kb / 1024 / 1024))
    
    if [[ $free_space_gb -lt 10 ]]; then
        log_message "ERROR" "Insufficient disk space: ${free_space_gb}GB available, 10GB required"
        return 1
    fi
    
    # Check memory usage
    local mem_usage
    mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [[ $mem_usage -gt 90 ]]; then
        log_message "WARN" "High memory usage: ${mem_usage}%"
    fi
    
    # Check internet connectivity
    if ! ping -c 1 arxiv.org >/dev/null 2>&1; then
        log_message "ERROR" "No internet connectivity to arxiv.org"
        return 1
    fi
    
    log_message "INFO" "System health check passed"
    return 0
}

# Create backup of current output
create_backup() {
    log_message "INFO" "Creating backup of current output"
    
    local backup_dir="${SCRIPT_DIR}/hepilot_output/backup/backup_${TIMESTAMP}"
    mkdir -p "$backup_dir"
    
    # Backup documents and metadata
    if [[ -d "${SCRIPT_DIR}/hepilot_output/documents" ]]; then
        cp -r "${SCRIPT_DIR}/hepilot_output/documents" "$backup_dir/"
        log_message "INFO" "Documents backed up to $backup_dir"
    fi
    
    # Backup state file
    if [[ -f "${SCRIPT_DIR}/hepilot_output/state.json" ]]; then
        cp "${SCRIPT_DIR}/hepilot_output/state.json" "$backup_dir/"
    fi
    
    # Cleanup old backups (keep last 7 days)
    find "${SCRIPT_DIR}/hepilot_output/backup" -type d -name "backup_*" -mtime +7 -exec rm -rf {} + 2>/dev/null || true
}

# Run the LHCb paper processor
# Returns: 0 if successful, 1 if failed
run_processor() {
    local retry_count=0
    local success=false
    
    while [[ $retry_count -lt $MAX_RETRIES ]] && [[ "$success" == false ]]; do
        log_message "INFO" "Starting LHCb paper processing (attempt $((retry_count + 1))/$MAX_RETRIES)"
        
        # Change to script directory
        cd "$SCRIPT_DIR"
        
        # Run the processor with timeout
        if timeout 7200 python run.py 2>&1 | tee -a "$LOG_FILE"; then
            log_message "INFO" "Processing completed successfully"
            success=true
        else
            local exit_code=$?
            retry_count=$((retry_count + 1))
            
            log_message "ERROR" "Processing failed with exit code $exit_code (attempt $retry_count/$MAX_RETRIES)" | tee -a "$ERROR_LOG"
            
            if [[ $retry_count -lt $MAX_RETRIES ]]; then
                log_message "INFO" "Retrying in $RETRY_DELAY seconds..."
                sleep $RETRY_DELAY
            fi
        fi
    done
    
    if [[ "$success" == true ]]; then
        return 0
    else
        log_message "ERROR" "Processing failed after $MAX_RETRIES attempts"
        return 1
    fi
}

# Monitor processing and handle interrupts
monitor_processing() {
    local last_health_check=0
    local last_backup=0
    local current_time
    
    while true; do
        current_time=$(date +%s)
        
        # Health check
        if [[ $((current_time - last_health_check)) -gt $HEALTH_CHECK_INTERVAL ]]; then
            if ! check_system_health; then
                log_message "ERROR" "System health check failed, stopping processing"
                cleanup_and_exit 1
            fi
            last_health_check=$current_time
        fi
        
        # Periodic backup
        if [[ $((current_time - last_backup)) -gt $BACKUP_INTERVAL ]]; then
            create_backup
            last_backup=$current_time
        fi
        
        # Run processor
        if run_processor; then
            log_message "INFO" "Processing cycle completed, waiting $UPDATE_INTERVAL seconds for next update"
            sleep $UPDATE_INTERVAL
        else
            log_message "ERROR" "Processing failed, waiting $((RETRY_DELAY * 2)) seconds before retry"
            sleep $((RETRY_DELAY * 2))
        fi
    done
}

# Cleanup resources and exit
# Args: exit_code (exit code to use)
cleanup_and_exit() {
    local exit_code=${1:-0}
    
    log_message "INFO" "Cleaning up and exiting with code $exit_code"
    
    # Remove PID file
    if [[ -f "$PID_FILE" ]]; then
        rm -f "$PID_FILE"
    fi
    
    # Deactivate virtual environment if active
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        deactivate 2>/dev/null || true
    fi
    
    exit $exit_code
}

# Handle interrupt signals
handle_interrupt() {
    log_message "WARN" "Received interrupt signal, initiating graceful shutdown"
    cleanup_and_exit 130
}

# Print usage information
print_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Automated LHCb ArXiv paper processing script for HEPilot

OPTIONS:
    -h, --help          Show this help message
    -d, --daemon        Run in daemon mode (continuous processing)
    -o, --once          Run processing once and exit
    -b, --backup        Create backup before processing
    -c, --check         Perform system health check only
    -s, --status        Show processing status
    --stop              Stop running daemon

EXAMPLES:
    $0 --once          # Process papers once and exit
    $0 --daemon        # Run continuously with updates
    $0 --check         # Check system health
    $0 --status        # Show current status

CONFIGURATION:
    Edit adapter_config.json to modify processing settings
    Logs are stored in: $LOG_DIR
    Output is stored in: ${SCRIPT_DIR}/hepilot_output

EOF
}

# Show current processing status
show_status() {
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_message "INFO" "LHCb processor is running (PID: $pid)"
        else
            log_message "WARN" "PID file exists but process is not running"
            rm -f "$PID_FILE"
        fi
    else
        log_message "INFO" "LHCb processor is not running"
    fi
    
    # Show processing statistics
    if [[ -f "${SCRIPT_DIR}/hepilot_output/state.json" ]]; then
        local state_info
        state_info=$(python -c "
import json
try:
    with open('${SCRIPT_DIR}/hepilot_output/state.json') as f:
        data = json.load(f)
    print(f\"Last run: {data.get('last_run', 'Never')}\")
    print(f\"Processed documents: {data.get('processed_count', 0)}\")
    print(f\"Last ArXiv ID: {data.get('last_arxiv_id', 'None')}\")
except Exception as e:
    print(f\"Error reading state: {e}\")
" 2>/dev/null)
        echo "$state_info"
    fi
}

# Stop running daemon
stop_daemon() {
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_message "INFO" "Stopping LHCb processor (PID: $pid)"
            kill -TERM "$pid"
            
            # Wait for graceful shutdown
            local count=0
            while kill -0 "$pid" 2>/dev/null && [[ $count -lt 30 ]]; do
                sleep 1
                count=$((count + 1))
            done
            
            if kill -0 "$pid" 2>/dev/null; then
                log_message "WARN" "Process did not stop gracefully, forcing shutdown"
                kill -KILL "$pid"
            fi
            
            rm -f "$PID_FILE"
            log_message "INFO" "LHCb processor stopped"
        else
            log_message "WARN" "PID file exists but process is not running"
            rm -f "$PID_FILE"
        fi
    else
        log_message "INFO" "LHCb processor is not running"
    fi
}

# Main execution

# Set up signal handlers
trap handle_interrupt SIGINT SIGTERM

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        print_usage
        exit 0
        ;;
    -c|--check)
        initialize_directories
        setup_environment
        check_system_health
        exit $?
        ;;
    -s|--status)
        show_status
        exit 0
        ;;
    --stop)
        stop_daemon
        exit 0
        ;;
    -b|--backup)
        initialize_directories
        create_backup
        exit 0
        ;;
    -o|--once)
        # Run once and exit
        log_message "INFO" "Starting single processing run"
        initialize_directories
        setup_environment || cleanup_and_exit 1
        check_system_health || cleanup_and_exit 1
        run_processor
        cleanup_and_exit $?
        ;;
    -d|--daemon|"")
        # Daemon mode (default)
        log_message "INFO" "Starting LHCb processor in daemon mode"
        
        # Check if already running
        if [[ -f "$PID_FILE" ]]; then
            local existing_pid
            existing_pid=$(cat "$PID_FILE")
            if kill -0 "$existing_pid" 2>/dev/null; then
                log_message "ERROR" "LHCb processor is already running (PID: $existing_pid)"
                exit 1
            else
                rm -f "$PID_FILE"
            fi
        fi
        
        # Store PID
        echo $$ > "$PID_FILE"
        
        # Initialize and start monitoring
        initialize_directories
        setup_environment || cleanup_and_exit 1
        check_system_health || cleanup_and_exit 1
        create_backup
        
        log_message "INFO" "LHCb processor daemon started (PID: $$)"
        monitor_processing
        ;;
    *)
        echo "Unknown option: $1"
        print_usage
        exit 1
        ;;
esac
