#!/bin/bash
#
# Compliance Snapshot - OpenAI Admin CLI
#
# Generates a comprehensive compliance snapshot of your entire OpenAI organization
# including users, projects, API keys, service accounts, and recent audit events.
# Perfect for compliance audits, security reviews, and documentation.
#
# Usage:
#   ./compliance-snapshot.sh [OPTIONS]
#
# Options:
#   --output-dir DIR      Directory to save reports (default: ./compliance-YYYYMMDD-HHMMSS)
#   --notify USER_ID      Send completion notification to user
#   --channel CHANNEL     Notification channel (mattermost, email)
#   --audit-days N        Days of audit logs to include (default: 30)
#   --help                Show this help message
#
# Examples:
#   # Generate snapshot with default settings
#   ./compliance-snapshot.sh
#
#   # Custom output directory
#   ./compliance-snapshot.sh --output-dir /path/to/compliance-reports
#
#   # Include 90 days of audit logs
#   ./compliance-snapshot.sh --audit-days 90
#
#   # Notify compliance team when complete
#   ./compliance-snapshot.sh --notify 49 --channel email
#
# Output:
#   Creates a directory with JSON files containing:
#   - users.json          - All organization users
#   - projects.json       - All projects (active and archived)
#   - admin-keys.json     - Admin API keys
#   - project-keys/       - Directory with per-project key inventories
#   - service-accounts/   - Directory with per-project service accounts
#   - audit-logs.json     - Recent audit events
#   - summary.txt         - Human-readable summary
#
# Environment:
#   OPENAI_ADMIN_KEY      Required: Your OpenAI Admin API key
#
# Author: Julian Billinger (ADMIN INTELLIGENCE)
# Version: 1.2.0
#

set -euo pipefail

# Default values
OUTPUT_DIR=""
NOTIFY_USER=""
NOTIFY_CHANNEL=""
AUDIT_DAYS=30
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/../.."
CLI_PATH="${PROJECT_ROOT}/openai_admin.py"

# Load .env file if it exists
ENV_FILE="${PROJECT_ROOT}/.env"
if [[ -f "$ENV_FILE" ]]; then
    # Export variables from .env file
    set -a
    source "$ENV_FILE"
    set +a
fi

# Activate virtual environment if it exists
VENV_PATH="${PROJECT_ROOT}/.venv"
if [[ -d "$VENV_PATH" ]]; then
    source "${VENV_PATH}/bin/activate"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Parse arguments
show_help() {
    grep '^#' "$0" | grep -v '#!/bin/bash' | sed 's/^# //' | sed 's/^#//'
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --notify)
            NOTIFY_USER="$2"
            shift 2
            ;;
        --channel)
            NOTIFY_CHANNEL="$2"
            shift 2
            ;;
        --audit-days)
            AUDIT_DAYS="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate environment
if [[ -z "${OPENAI_ADMIN_KEY:-}" ]]; then
    echo -e "${RED}Error: OPENAI_ADMIN_KEY environment variable not set${NC}"
    echo "Export your Admin API key: export OPENAI_ADMIN_KEY='sk-admin-...'"
    exit 1
fi

if [[ ! -f "$CLI_PATH" ]]; then
    echo -e "${RED}Error: CLI script not found at $CLI_PATH${NC}"
    exit 1
fi

# Create output directory
if [[ -z "$OUTPUT_DIR" ]]; then
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    OUTPUT_DIR="./compliance-snapshot-$TIMESTAMP"
fi

mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/project-keys"
mkdir -p "$OUTPUT_DIR/service-accounts"

echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║       OpenAI Admin - Compliance Snapshot Generator            ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Snapshot Date:${NC} $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "${YELLOW}Output Directory:${NC} $OUTPUT_DIR"
echo -e "${YELLOW}Audit Period:${NC} Last ${AUDIT_DAYS} days"
echo ""

# Initialize summary
SUMMARY_FILE="$OUTPUT_DIR/summary.txt"
{
    echo "========================================================================"
    echo "  OpenAI Organization Compliance Snapshot"
    echo "========================================================================"
    echo ""
    echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Audit Period: Last ${AUDIT_DAYS} days"
    echo ""
} > "$SUMMARY_FILE"

# Function to run command and save output
collect_data() {
    local description="$1"
    local output_file="$2"
    shift 2
    
    echo -e "${GREEN}▶ ${description}${NC}"
    
    if python3 "$CLI_PATH" "$@" --format json > "$output_file" 2>/dev/null; then
        echo -e "${GREEN}  ✓ Saved to: $(basename "$output_file")${NC}"
        return 0
    else
        echo -e "${RED}  ✗ Failed${NC}"
        return 1
    fi
}

# SECTION 1: Organization Structure
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 1: ORGANIZATION STRUCTURE${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

collect_data "Collecting Users" "$OUTPUT_DIR/users.json" users list
USER_COUNT=$(grep -c '"id":' "$OUTPUT_DIR/users.json" 2>/dev/null || echo "0")
echo ""

collect_data "Collecting Projects (including archived)" "$OUTPUT_DIR/projects.json" projects list --include-archived
PROJECT_COUNT=$(grep -c '"id":' "$OUTPUT_DIR/projects.json" 2>/dev/null || echo "0")
echo ""

# Add to summary
{
    echo "========================================================================"
    echo "  ORGANIZATION OVERVIEW"
    echo "========================================================================"
    echo ""
    echo "Total Users: $USER_COUNT"
    echo "Total Projects: $PROJECT_COUNT"
    echo ""
} >> "$SUMMARY_FILE"

# SECTION 2: API Keys
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 2: API KEY INVENTORY${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

collect_data "Collecting Admin Keys" "$OUTPUT_DIR/admin-keys.json" keys list-admin
ADMIN_KEY_COUNT=$(grep -c '"id":' "$OUTPUT_DIR/admin-keys.json" 2>/dev/null || echo "0")
echo ""

# Collect project keys
TOTAL_PROJECT_KEYS=0
if [[ -f "$OUTPUT_DIR/projects.json" ]]; then
    PROJECT_IDS=$(grep -o '"id": *"[^"]*"' "$OUTPUT_DIR/projects.json" | sed 's/"id": *"\([^"]*\)"/\1/')
    
    if [[ -n "$PROJECT_IDS" ]]; then
        while IFS= read -r project_id; do
            if [[ -n "$project_id" ]]; then
                PROJECT_NAME=$(grep -A 5 "\"id\": *\"$project_id\"" "$OUTPUT_DIR/projects.json" | grep -o '"name": *"[^"]*"' | head -1 | sed 's/"name": *"\([^"]*\)"/\1/' || echo "$project_id")
                
                echo -e "${YELLOW}Collecting keys for: $PROJECT_NAME${NC}"
                
                if collect_data "  Project Keys" "$OUTPUT_DIR/project-keys/${project_id}.json" keys list-project "$project_id"; then
                    KEY_COUNT=$(grep -c '"id":' "$OUTPUT_DIR/project-keys/${project_id}.json" 2>/dev/null || echo "0")
                    KEY_COUNT=$(echo "$KEY_COUNT" | tr -d '\n\r ')
                    ((TOTAL_PROJECT_KEYS += KEY_COUNT))
                fi
                echo ""
            fi
        done <<< "$PROJECT_IDS"
    fi
fi

# Add to summary
{
    echo "========================================================================"
    echo "  API KEYS"
    echo "========================================================================"
    echo ""
    echo "Admin Keys: $ADMIN_KEY_COUNT"
    echo "Project Keys: $TOTAL_PROJECT_KEYS"
    echo "Total Keys: $((ADMIN_KEY_COUNT + TOTAL_PROJECT_KEYS))"
    echo ""
} >> "$SUMMARY_FILE"

# SECTION 3: Service Accounts
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 3: SERVICE ACCOUNTS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

TOTAL_SERVICE_ACCOUNTS=0
if [[ -f "$OUTPUT_DIR/projects.json" ]]; then
    PROJECT_IDS=$(grep -o '"id": *"[^"]*"' "$OUTPUT_DIR/projects.json" | sed 's/"id": *"\([^"]*\)"/\1/')
    
    if [[ -n "$PROJECT_IDS" ]]; then
        while IFS= read -r project_id; do
            if [[ -n "$project_id" ]]; then
                PROJECT_NAME=$(grep -A 5 "\"id\": *\"$project_id\"" "$OUTPUT_DIR/projects.json" | grep -o '"name": *"[^"]*"' | head -1 | sed 's/"name": *"\([^"]*\)"/\1/' || echo "$project_id")
                
                echo -e "${YELLOW}Collecting service accounts for: $PROJECT_NAME${NC}"
                
                if collect_data "  Service Accounts" "$OUTPUT_DIR/service-accounts/${project_id}.json" service-accounts list "$project_id"; then
                    SA_COUNT=$(grep -c '"id":' "$OUTPUT_DIR/service-accounts/${project_id}.json" 2>/dev/null || echo "0")
                    SA_COUNT=$(echo "$SA_COUNT" | tr -d '\n\r ')
                    ((TOTAL_SERVICE_ACCOUNTS += SA_COUNT))
                fi
                echo ""
            fi
        done <<< "$PROJECT_IDS"
    fi
fi

# Add to summary
{
    echo "========================================================================"
    echo "  SERVICE ACCOUNTS"
    echo "========================================================================"
    echo ""
    echo "Total Service Accounts: $TOTAL_SERVICE_ACCOUNTS"
    echo ""
} >> "$SUMMARY_FILE"

# SECTION 4: Audit Logs
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 4: AUDIT LOGS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

collect_data "Collecting Audit Logs (${AUDIT_DAYS} days)" "$OUTPUT_DIR/audit-logs.json" audit list --days "$AUDIT_DAYS" --limit 500
AUDIT_EVENT_COUNT=$(grep -c '"id":' "$OUTPUT_DIR/audit-logs.json" 2>/dev/null || echo "0")
echo ""

# Add to summary
{
    echo "========================================================================"
    echo "  AUDIT EVENTS"
    echo "========================================================================"
    echo ""
    echo "Audit Period: Last ${AUDIT_DAYS} days"
    echo "Total Events: $AUDIT_EVENT_COUNT"
    echo ""
} >> "$SUMMARY_FILE"

# Create manifest file
MANIFEST_FILE="$OUTPUT_DIR/manifest.json"
cat > "$MANIFEST_FILE" << EOF
{
  "snapshot_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "snapshot_version": "1.2.0",
  "audit_days": $AUDIT_DAYS,
  "statistics": {
    "users": $USER_COUNT,
    "projects": $PROJECT_COUNT,
    "admin_keys": $ADMIN_KEY_COUNT,
    "project_keys": $TOTAL_PROJECT_KEYS,
    "total_keys": $((ADMIN_KEY_COUNT + TOTAL_PROJECT_KEYS)),
    "service_accounts": $TOTAL_SERVICE_ACCOUNTS,
    "audit_events": $AUDIT_EVENT_COUNT
  },
  "files": {
    "users": "users.json",
    "projects": "projects.json",
    "admin_keys": "admin-keys.json",
    "project_keys_dir": "project-keys/",
    "service_accounts_dir": "service-accounts/",
    "audit_logs": "audit-logs.json",
    "summary": "summary.txt"
  }
}
EOF

# Finalize summary
{
    echo "========================================================================"
    echo "  FILES GENERATED"
    echo "========================================================================"
    echo ""
    echo "manifest.json         - Snapshot metadata and statistics"
    echo "summary.txt           - This summary file"
    echo "users.json            - Organization users"
    echo "projects.json         - All projects"
    echo "admin-keys.json       - Admin API keys"
    echo "project-keys/         - Project-specific keys"
    echo "service-accounts/     - Service accounts per project"
    echo "audit-logs.json       - Audit events"
    echo ""
    echo "========================================================================"
    echo "  SNAPSHOT COMPLETE"
    echo "========================================================================"
    echo ""
    echo "Location: $OUTPUT_DIR"
    echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
} >> "$SUMMARY_FILE"

# Display summary
echo ""
echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║                    Snapshot Complete                           ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
cat "$SUMMARY_FILE"

# Send notification if requested
if [[ -n "$NOTIFY_USER" ]] && [[ -n "$NOTIFY_CHANNEL" ]]; then
    echo -e "${GREEN}Sending completion notification...${NC}"
    python3 "$CLI_PATH" notify test "$NOTIFY_USER" --channel "$NOTIFY_CHANNEL" \
        --message "Compliance snapshot complete. Location: $OUTPUT_DIR. Files: $((USER_COUNT + PROJECT_COUNT + ADMIN_KEY_COUNT + TOTAL_PROJECT_KEYS + TOTAL_SERVICE_ACCOUNTS + AUDIT_EVENT_COUNT)) data points collected." 2>/dev/null || true
    echo -e "${GREEN}✓ Notification sent to user $NOTIFY_USER via $NOTIFY_CHANNEL${NC}"
fi

echo ""
echo -e "${YELLOW}📋 NEXT STEPS:${NC}"
echo ""
echo -e "  1. Review summary.txt for overview"
echo -e "  2. Archive snapshot for compliance records"
echo -e "  3. Compare with previous snapshots for changes"
echo -e "  4. Share with compliance/security team as needed"
echo ""
echo -e "${YELLOW}🔒 COMPLIANCE TIPS:${NC}"
echo ""
echo -e "  • Run monthly snapshots for audit trail"
echo -e "  • Store snapshots securely (encrypted, access-controlled)"
echo -e "  • Document any anomalies or changes"
echo -e "  • Use for SOC 2, ISO 27001, or internal audits"
echo -e "  • Compare snapshots to detect unauthorized changes"
echo ""
