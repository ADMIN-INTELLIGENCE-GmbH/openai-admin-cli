#!/bin/bash
#
# Weekly Cost Report - OpenAI Admin CLI
#
# Generates a comprehensive weekly cost breakdown with project-level and
# line-item analysis to track spending trends.
#
# Usage:
#   ./weekly-cost-report.sh [OPTIONS]
#
# Options:
#   --days N              Number of days to report (default: 7)
#   --notify USER_ID      Send results to user via notification
#   --channel CHANNEL     Notification channel (mattermost, email)
#   --format FORMAT       Output format: table or json (default: table)
#   --project-id ID       Filter by specific project (can be repeated)
#   --help                Show this help message
#
# Examples:
#   # Last 7 days
#   ./weekly-cost-report.sh
#
#   # Last 30 days
#   ./weekly-cost-report.sh --days 30
#
#   # Specific project only
#   ./weekly-cost-report.sh --project-id proj_abc123
#
#   # Send to user via email
#   ./weekly-cost-report.sh --notify 49 --channel email
#
# Environment:
#   OPENAI_ADMIN_KEY      Required: Your OpenAI Admin API key
#
# Author: Julian Billinger (ADMIN INTELLIGENCE)
# Version: 1.2.0
#

set -euo pipefail

# Default values
DAYS=7
NOTIFY_USER=""
NOTIFY_CHANNEL=""
FORMAT="table"
PROJECT_IDS=()
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
        --days)
            DAYS="$2"
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
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --project-id)
            PROJECT_IDS+=("$2")
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

# Build project filter flags
PROJECT_FLAGS=""
if [[ ${#PROJECT_IDS[@]} -gt 0 ]]; then
    for project_id in "${PROJECT_IDS[@]}"; do
        PROJECT_FLAGS="$PROJECT_FLAGS --project-id $project_id"
    done
fi

# Print header
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          OpenAI Admin - Weekly Cost Report                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Report Period:${NC} Last ${DAYS} day(s)"
echo -e "${YELLOW}Generated:${NC} $(date '+%Y-%m-%d %H:%M:%S')"
if [[ ${#PROJECT_IDS[@]} -gt 0 ]]; then
    echo -e "${YELLOW}Projects:${NC} ${PROJECT_IDS[*]}"
fi
echo ""

# Function to run command with error handling
run_command() {
    local description="$1"
    shift
    
    echo -e "${GREEN}▶ ${description}${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if python3 "$CLI_PATH" $NOTIFY_FLAGS "$@" --format "$FORMAT" --days "$DAYS" $PROJECT_FLAGS; then
        echo ""
    else
        echo -e "${RED}✗ Command failed${NC}"
        echo ""
    fi
}

# Run cost reports
echo -e "${CYAN}📊 OVERALL COSTS${NC}"
echo ""
run_command "Total Costs - All Projects" costs

echo -e "${CYAN}📁 COSTS BY PROJECT${NC}"
echo ""
run_command "Costs Grouped by Project" costs --group-by project_id

echo -e "${CYAN}🔍 DETAILED LINE ITEM BREAKDOWN${NC}"
echo ""
run_command "Costs by Project and Line Item" costs --group-by project_id --group-by line_item

# Summary footer
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Report Complete                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

if [[ -n "$NOTIFY_USER" ]]; then
    echo -e "${GREEN}✓ Notifications sent to user $NOTIFY_USER via $NOTIFY_CHANNEL${NC}"
fi

echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo -e "  • For usage details, run: ./daily-usage-report.sh --days ${DAYS}"
echo -e "  • For monthly summary, run: ./monthly-billing-summary.sh"
echo -e "  • Set up alerts: ./cost-alert-check.sh (coming soon)"
echo ""
