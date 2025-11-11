#!/bin/bash
#
# List All Keys - OpenAI Admin CLI
#
# Generates a complete inventory of all API keys across the organization,
# including admin keys and project-specific keys for all projects.
#
# Usage:
#   ./list-all-keys.sh [OPTIONS]
#
# Options:
#   --notify USER_ID      Send results to user via notification
#   --channel CHANNEL     Notification channel (mattermost, email)
#   --format FORMAT       Output format: table or json (default: table)
#   --output FILE         Save output to file (JSON format recommended)
#   --help                Show this help message
#
# Examples:
#   # Display all keys
#   ./list-all-keys.sh
#
#   # Save to file for audit
#   ./list-all-keys.sh --output key-inventory-$(date +%Y%m%d).json --format json
#
#   # Send to security team
#   ./list-all-keys.sh --notify 49 --channel email
#
# Environment:
#   OPENAI_ADMIN_KEY      Required: Your OpenAI Admin API key
#
# Author: Julian Billinger (ADMIN INTELLIGENCE)
# Version: 1.2.0
#

set -euo pipefail

# Default values
NOTIFY_USER=""
NOTIFY_CHANNEL=""
FORMAT="table"
OUTPUT_FILE=""
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
NC='\033[0m' # No Color

# Parse arguments
show_help() {
    grep '^#' "$0" | grep -v '#!/bin/bash' | sed 's/^# //' | sed 's/^#//'
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --notify)
            NOTIFY_USER="$2"
            shift 2
            ;;
        --channel)
            NOTIFY_CHANNEL="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
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

# Build notification flags
NOTIFY_FLAGS=""
if [[ -n "$NOTIFY_USER" ]] && [[ -n "$NOTIFY_CHANNEL" ]]; then
    NOTIFY_FLAGS="--notify $NOTIFY_USER --channel $NOTIFY_CHANNEL"
fi

# Setup output redirection
if [[ -n "$OUTPUT_FILE" ]]; then
    exec > >(tee "$OUTPUT_FILE")
    echo -e "${GREEN}✓ Output will be saved to: $OUTPUT_FILE${NC}"
    echo ""
fi

# Print header
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          OpenAI Admin - Complete Key Inventory                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Generated:${NC} $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Function to run command with error handling
run_command() {
    local description="$1"
    shift
    
    echo -e "${GREEN}▶ ${description}${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if python3 "$CLI_PATH" $NOTIFY_FLAGS "$@" --format "$FORMAT"; then
        echo ""
        return 0
    else
        echo -e "${YELLOW}⚠ No data or command failed${NC}"
        echo ""
        return 1
    fi
}

# SECTION 1: Admin Keys
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 1: ADMIN API KEYS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

run_command "Organization Admin Keys" keys list-admin --limit 100

# SECTION 2: Project Keys
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 2: PROJECT API KEYS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

# Get list of projects
echo -e "${YELLOW}Fetching project list...${NC}"
PROJECTS_JSON=$(python3 "$CLI_PATH" projects list --format json 2>/dev/null)

if [[ -n "$PROJECTS_JSON" ]]; then
    # Extract project IDs using grep and sed (more portable than jq)
    PROJECT_IDS=$(echo "$PROJECTS_JSON" | grep -o '"id": *"[^"]*"' | sed 's/"id": *"\([^"]*\)"/\1/')
    
    if [[ -n "$PROJECT_IDS" ]]; then
        PROJECT_COUNT=0
        while IFS= read -r project_id; do
            if [[ -n "$project_id" ]]; then
                ((PROJECT_COUNT++))
                
                # Get project name (try to extract it, fallback to ID)
                PROJECT_NAME=$(echo "$PROJECTS_JSON" | grep -A 5 "\"id\": *\"$project_id\"" | grep -o '"name": *"[^"]*"' | head -1 | sed 's/"name": *"\([^"]*\)"/\1/' || echo "$project_id")
                
                echo -e "${YELLOW}Project:${NC} $PROJECT_NAME (ID: $project_id)"
                echo ""
                
                run_command "Keys for $PROJECT_NAME" keys list-project "$project_id" --limit 100
                
                # Also list service accounts for this project
                run_command "Service Accounts for $PROJECT_NAME" service-accounts list "$project_id" --limit 100
            fi
        done <<< "$PROJECT_IDS"
        
        echo -e "${GREEN}✓ Scanned $PROJECT_COUNT project(s)${NC}"
    else
        echo -e "${YELLOW}⚠ No projects found${NC}"
    fi
else
    echo -e "${RED}✗ Failed to fetch projects${NC}"
fi

echo ""

# Summary footer
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Inventory Complete                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

if [[ -n "$OUTPUT_FILE" ]]; then
    echo -e "${GREEN}✓ Results saved to: $OUTPUT_FILE${NC}"
fi

if [[ -n "$NOTIFY_USER" ]]; then
    echo -e "${GREEN}✓ Report sent to user $NOTIFY_USER via $NOTIFY_CHANNEL${NC}"
fi

echo ""
echo -e "${YELLOW}📊 KEY INVENTORY TIPS:${NC}"
echo ""
echo -e "  • Review last used dates to find stale keys"
echo -e "  • Check for keys without names (may be forgotten test keys)"
echo -e "  • Verify service account keys are documented"
echo -e "  • Run unused keys report: ./unused-keys-report.sh"
echo ""
echo -e "${YELLOW}🔒 SECURITY BEST PRACTICES:${NC}"
echo ""
echo -e "  • Rotate keys regularly (quarterly recommended)"
echo -e "  • Delete unused or test keys immediately"
echo -e "  • Use service accounts for production systems"
echo -e "  • Document key ownership and purpose"
echo -e "  • Monitor key usage in audit logs"
echo ""
