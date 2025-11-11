#!/bin/bash
#
# Monthly Billing Summary - OpenAI Admin CLI
#
# Generates a comprehensive end-of-month summary including costs, usage,
# active projects, and recommendations before the billing cycle.
#
# Usage:
#   ./monthly-billing-summary.sh [OPTIONS]
#
# Options:
#   --days N              Number of days to report (default: 30)
#   --notify USER_ID      Send results to user via notification
#   --channel CHANNEL     Notification channel (mattermost, email)
#   --format FORMAT       Output format: table or json (default: table)
#   --help                Show this help message
#
# Examples:
#   # Last 30 days (default)
#   ./monthly-billing-summary.sh
#
#   # Last 60 days for comparison
#   ./monthly-billing-summary.sh --days 60
#
#   # Send to finance team via email
#   ./monthly-billing-summary.sh --notify 49 --channel email
#
# Environment:
#   OPENAI_ADMIN_KEY      Required: Your OpenAI Admin API key
#
# Author: Julian Billinger (ADMIN INTELLIGENCE)
# Version: 1.2.0
#

set -euo pipefail

# Default values
DAYS=30
NOTIFY_USER=""
NOTIFY_CHANNEL=""
FORMAT="table"
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

# Print header
echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║       OpenAI Admin - Monthly Billing Summary                  ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Report Period:${NC} Last ${DAYS} day(s)"
echo -e "${YELLOW}Generated:${NC} $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "${YELLOW}Month:${NC} $(date '+%B %Y')"
echo ""

# Function to run command with error handling
run_command() {
    local description="$1"
    shift
    
    echo -e "${GREEN}▶ ${description}${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if python3 "$CLI_PATH" $NOTIFY_FLAGS "$@" --format "$FORMAT"; then
        echo ""
    else
        echo -e "${RED}✗ Command failed${NC}"
        echo ""
    fi
}

# SECTION 1: Organization Overview
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 1: ORGANIZATION OVERVIEW${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

run_command "Active Projects" projects list
run_command "Organization Users" users list

# SECTION 2: Cost Analysis
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 2: COST ANALYSIS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

run_command "Total Costs (Last ${DAYS} Days)" costs --days "$DAYS"
run_command "Costs by Project" costs --days "$DAYS" --group-by project_id
run_command "Costs by Line Item" costs --days "$DAYS" --group-by line_item

# SECTION 3: Usage Summary
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 3: USAGE SUMMARY${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

run_command "Completions Usage by Project" usage completions --days "$DAYS" --group-by project_id
run_command "Completions Usage by Model" usage completions --days "$DAYS" --group-by model
run_command "Image Generation Usage" usage images --days "$DAYS" --group-by project_id --group-by model
run_command "Embeddings Usage" usage embeddings --days "$DAYS" --group-by project_id

# SECTION 4: Security & Compliance
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 4: SECURITY & COMPLIANCE${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

run_command "Recent Audit Events (Last 7 Days)" audit list --days 7 --limit 20

# Summary footer
echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║                    Monthly Summary Complete                    ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"

if [[ -n "$NOTIFY_USER" ]]; then
    echo -e "${GREEN}✓ Full report sent to user $NOTIFY_USER via $NOTIFY_CHANNEL${NC}"
fi

echo ""
echo -e "${YELLOW}📋 RECOMMENDATIONS:${NC}"
echo ""
echo -e "  1. Review costs by project to identify optimization opportunities"
echo -e "  2. Check for unused API keys: ./unused-keys-report.sh"
echo -e "  3. Review rate limits for cost control"
echo -e "  4. Run security scan: ./audit-security-scan.sh"
echo -e "  5. Archive inactive projects to reduce clutter"
echo ""
echo -e "${YELLOW}📅 Next Steps:${NC}"
echo -e "  • Schedule weekly cost reports: ./weekly-cost-report.sh"
echo -e "  • Set up daily monitoring: ./daily-usage-report.sh"
echo -e "  • Regular security audits: ./audit-security-scan.sh"
echo ""
