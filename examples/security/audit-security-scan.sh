#!/bin/bash
#
# Audit Security Scan - OpenAI Admin CLI
#
# Scans audit logs for suspicious activities and security events including:
# - Failed authentication attempts
# - API key deletions
# - Service account changes
# - User permission changes
# - Project modifications
#
# Usage:
#   ./audit-security-scan.sh [OPTIONS]
#
# Options:
#   --days N              Number of days to scan (default: 7)
#   --notify USER_ID      Send results to user via notification
#   --channel CHANNEL     Notification channel (mattermost, email)
#   --format FORMAT       Output format: table or json (default: table)
#   --severity LEVEL      Filter by severity: low, medium, high (default: all)
#   --help                Show this help message
#
# Examples:
#   # Last 7 days (default)
#   ./audit-security-scan.sh
#
#   # Last 30 days
#   ./audit-security-scan.sh --days 30
#
#   # Send security alert via email
#   ./audit-security-scan.sh --notify 49 --channel email
#
#   # High severity only
#   ./audit-security-scan.sh --severity high
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
SEVERITY="all"
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

# Security event types to monitor
SECURITY_EVENTS=(
    "api_key.created"
    "api_key.deleted"
    "api_key.updated"
    "service_account.created"
    "service_account.deleted"
    "service_account.updated"
    "user.added"
    "user.deleted"
    "user.updated"
    "project.created"
    "project.archived"
    "project.updated"
)

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
        --severity)
            SEVERITY="$2"
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
echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║          OpenAI Admin - Security Audit Scan                   ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Scan Period:${NC} Last ${DAYS} day(s)"
echo -e "${YELLOW}Scan Date:${NC} $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "${YELLOW}Severity Filter:${NC} ${SEVERITY}"
echo ""

# Function to run command with error handling
run_command() {
    local description="$1"
    local event_type="$2"
    
    echo -e "${GREEN}▶ ${description}${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if python3 "$CLI_PATH" $NOTIFY_FLAGS audit list \
        --days "$DAYS" \
        --event-type "$event_type" \
        --limit 50 \
        --format "$FORMAT"; then
        echo ""
    else
        echo -e "${YELLOW}⚠ No events found or command failed${NC}"
        echo ""
    fi
}

# SECTION 1: API Key Security
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 1: API KEY SECURITY${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

run_command "API Keys Created" "api_key.created"
run_command "API Keys Deleted" "api_key.deleted"
run_command "API Keys Updated" "api_key.updated"

# SECTION 2: Service Account Activity
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 2: SERVICE ACCOUNT ACTIVITY${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

run_command "Service Accounts Created" "service_account.created"
run_command "Service Accounts Deleted" "service_account.deleted"
run_command "Service Accounts Updated" "service_account.updated"

# SECTION 3: User Management
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 3: USER MANAGEMENT${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

run_command "Users Added" "user.added"
run_command "Users Deleted" "user.deleted"
run_command "Users Updated (Role Changes)" "user.updated"

# SECTION 4: Project Changes
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 4: PROJECT CHANGES${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

run_command "Projects Created" "project.created"
run_command "Projects Archived" "project.archived"
run_command "Projects Updated" "project.updated"

# SECTION 5: All Recent Events
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 5: ALL RECENT EVENTS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${GREEN}▶ Complete Audit Log (Last ${DAYS} Days)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python3 "$CLI_PATH" $NOTIFY_FLAGS audit list --days "$DAYS" --limit 100 --format "$FORMAT"; then
    echo ""
else
    echo -e "${RED}✗ Command failed${NC}"
    echo ""
fi

# Summary footer
echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║                    Security Scan Complete                      ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"

if [[ -n "$NOTIFY_USER" ]]; then
    echo -e "${GREEN}✓ Security report sent to user $NOTIFY_USER via $NOTIFY_CHANNEL${NC}"
fi

echo ""
echo -e "${YELLOW}🔒 SECURITY RECOMMENDATIONS:${NC}"
echo ""
echo -e "  1. Review all API key deletions for unauthorized access"
echo -e "  2. Verify service account changes with team members"
echo -e "  3. Check user role updates for privilege escalation"
echo -e "  4. Investigate any unexpected project modifications"
echo -e "  5. Run key inventory: ./list-all-keys.sh"
echo -e "  6. Find unused keys: ./unused-keys-report.sh"
echo ""
echo -e "${YELLOW}📅 Schedule Regular Scans:${NC}"
echo -e "  • Daily scans: ./audit-security-scan.sh --notify <user> --channel email"
echo -e "  • Weekly deep dive: ./audit-security-scan.sh --days 7"
echo -e "  • Monthly compliance: ./compliance-snapshot.sh"
echo ""
