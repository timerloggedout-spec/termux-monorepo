#!/bin/bash

# Sync Developer Roadmap Content
# Syncs content from nilbuild/developer-roadmap to local roadmaps/ directory

set -euo pipefail

# Configuration
UPSTREAM_REPO="nilbuild/developer-roadmap"
UPSTREAM_URL="https://github.com/${UPSTREAM_REPO}.git"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMP_DIR="${LOCAL_DIR}/.sync-temp"
LOG_FILE="${LOCAL_DIR}/sync/sync-log.json"
CONFIG_FILE="${LOCAL_DIR}/sync/sync-config.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load config
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        log_info "Loading config from $CONFIG_FILE"
        UPSTREAM_REPO=$(jq -r '.upstream_repo // "nilbuild/developer-roadmap"' "$CONFIG_FILE")
        UPSTREAM_URL="https://github.com/${UPSTREAM_REPO}.git"
        SYNC_DEPTH=$(jq -r '.sync_depth // 1' "$CONFIG_FILE")
        SYNC_BRANCH=$(jq -r '.sync_branch // "master"' "$CONFIG_FILE")
    fi
}

# Save config
save_config() {
    cat > "$CONFIG_FILE" <<EOF
{
  "upstream_repo": "${UPSTREAM_REPO}",
  "sync_branch": "${SYNC_BRANCH:-master}",
  "sync_depth": ${SYNC_DEPTH:-1},
  "last_sync": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "sync_count": $(( ${SYNC_COUNT:-0} + 1 ))
}
EOF
}

# Initialize log
init_log() {
    if [ ! -f "$LOG_FILE" ]; then
        cat > "$LOG_FILE" <<EOF
{
  "syncs": []
}
EOF
    fi
}

# Record sync
record_sync() {
    local status="$1"
    local duration="$2"
    local files_updated="$3"
    local files_added="$4"
    local files_removed="$5"
    local timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    
    # Read existing logs
    local existing=$(cat "$LOG_FILE")
    
    # Create new entry
    local new_entry=$(jq -n \
        --arg ts "$timestamp" \
        --arg status "$status" \
        --argjson duration "$duration" \
        --argjson updated "$files_updated" \
        --argjson added "$files_added" \
        --argjson removed "$files_removed" \
        '{
            "timestamp": $ts,
            "status": $status,
            "duration_ms": $duration,
            "files": {
                "updated": $updated,
                "added": $added,
                "removed": $removed
            }
        }')
    
    # Append to logs
    echo "$existing" | jq --argjson entry "$new_entry" '.syncs += [$entry]' > "$LOG_FILE"
}

# Cleanup temp directory
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi
}

trap cleanup EXIT

# Main sync function
sync_content() {
    local force="$1"
    
    log_info "Starting sync from ${UPSTREAM_REPO}..."
    local start_time=$(date +%s%N)
    
    # Create temp directory
    mkdir -p "$TEMP_DIR"
    
    # Clone upstream
    log_info "Cloning ${UPSTREAM_REPO}..."
    if [ "$force" = "true" ]; then
        git clone --depth 1 --branch "${SYNC_BRANCH:-master}" "$UPSTREAM_URL" "$TEMP_DIR" 2>&1 | while read line; do
            log_info "  $line"
        done
    else
        # Try shallow clone first, fallback to full if needed
        if ! git clone --depth "${SYNC_DEPTH:-1}" --branch "${SYNC_BRANCH:-master}" "$UPSTREAM_URL" "$TEMP_DIR" 2>&1 | while read line; do
            log_info "  $line"
        done; then
            log_warning "Shallow clone failed, trying full clone..."
            git clone --branch "${SYNC_BRANCH:-master}" "$UPSTREAM_URL" "$TEMP_DIR" 2>&1 | while read line; do
                log_info "  $line"
            done
        fi
    fi
    
    # Create target directories
    mkdir -p "${LOCAL_DIR}/content" "${LOCAL_DIR}/questions"
    
    # Sync roadmaps
    log_info "Syncing roadmaps..."
    if [ -d "$TEMP_DIR/roadmaps" ]; then
        # Copy roadmap content (excluding node_modules, .git, etc.)
        rsync -a --exclude='.git' --exclude='node_modules' --exclude='.DS_Store' \
            "$TEMP_DIR/roadmaps/" "${LOCAL_DIR}/content/" 2>/dev/null || {
            # Fallback to cp if rsync not available
            cp -r "$TEMP_DIR/roadmaps/." "${LOCAL_DIR}/content/" 2>/dev/null || {
                log_error "Failed to copy roadmap content"
                return 1
            }
        }
    fi
    
    # Sync questions
    log_info "Syncing questions..."
    if [ -d "$TEMP_DIR/questions" ]; then
        rsync -a --exclude='.git' --exclude='node_modules' --exclude='.DS_Store' \
            "$TEMP_DIR/questions/" "${LOCAL_DIR}/questions/" 2>/dev/null || {
            cp -r "$TEMP_DIR/questions/." "${LOCAL_DIR}/questions/" 2>/dev/null || {
                log_error "Failed to copy questions"
                return 1
            }
        }
    fi
    
    # Count changes
    local files_updated=0
    local files_added=0
    local files_removed=0
    
    # This is a simplified approach - in production, use git diff
    log_info "Calculating changes..."
    
    # Calculate duration
    local end_time=$(date +%s%N)
    local duration_ms=$(( (end_time - start_time) / 1000000 ))
    
    log_success "Sync completed in ${duration_ms}ms"
    
    # Record sync
    record_sync "success" "$duration_ms" "$files_updated" "$files_added" "$files_removed"
    
    return 0
}

# Update metadata
update_metadata() {
    log_info "Updating metadata..."
    
    # Generate roadmap index
    local index_file="${LOCAL_DIR}/metadata/roadmap-index.json"
    mkdir -p "${LOCAL_DIR}/metadata"
    
    # Count roadmaps and topics
    local roadmap_count=$(find "${LOCAL_DIR}/content" -maxdepth 1 -type d | wc -l)
    roadmap_count=$((roadmap_count - 1)) # Subtract the . directory
    
    local total_topics=0
    local total_questions=0
    
    # Generate index
    cat > "$index_file" <<EOF
{
  "version": "1.0.0",
  "generated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "roadmaps": {},
  "stats": {
    "total_roadmaps": ${roadmap_count},
    "total_nodes": 0,
    "total_questions": 0
  }
}
EOF
    
    log_success "Metadata updated"
}

# Main execution
main() {
    local force="false"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --upstream)
                UPSTREAM_REPO="$2"
                UPSTREAM_URL="https://github.com/${UPSTREAM_REPO}.git"
                shift 2
                ;;
            --branch)
                SYNC_BRANCH="$2"
                shift 2
                ;;
            --depth)
                SYNC_DEPTH="$2"
                shift 2
                ;;
            --force)
                force="true"
                shift
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Load config
    load_config
    
    # Initialize log
    init_log
    
    # Perform sync
    if sync_content "$force"; then
        # Update metadata
        update_metadata
        
        # Save config
        save_config
        
        log_success "Sync completed successfully!"
        exit 0
    else
        log_error "Sync failed!"
        record_sync "failed" "0" "0" "0" "0"
        exit 1
    fi
}

main "$@"
