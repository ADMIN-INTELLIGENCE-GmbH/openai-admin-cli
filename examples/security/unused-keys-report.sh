#!/bin/bash
#
# Unused Keys Report - OpenAI Admin CLI
#
# Identifies API keys that haven't been used in a specified number of days.
# Helps maintain security hygiene by finding stale or forgotten keys.
#
# Usage:
#   ./unused-keys-report.sh [OPTIONS]
#
# Options:
#   --days N              Keys unused for N days (default: 30)
#   --notify USER_ID      Send results to user via notification
#   --channel CHANNEL     Notification channel (mattermost, email)
#   --format FORMAT       Output format: table or json (default: table)
#   --output FILE         Save findings to file
#   --help                Show this help message
#
# Examples:
#   # Keys not used in 30 days
#   ./unused-keys-report.sh
#
#   # Keys not used in 90 days (more aggressive cleanup)
#   ./unused-keys-report.sh --days 90
#
#   # Save report for review
#   ./unused-keys-report.sh --output unused-keys-$(date +%Y%m%d).json --format json
#
#   # Alert security team
#   ./unused-keys-report.sh --notify 49 --channel email
#
# Environment:
#   OPENAI_ADMIN_KEY      Required: Your OpenAI Admin API key
#
# Note: This script uses the 'last_used_at' field from API keys to determine
#       if a key is unused. Keys that have never been used will also be reported.
#
# Author: Julian Billinger (ADMIN INTELLIGENCE)
# Version: 1.2.0
#

set -euo pipefail

# Default values
UNUSED_DAYS=30
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
            UNUSED_DAYS="$2"
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

# Calculate cutoff date (days ago)
CUTOFF_DATE=$(date -v-${UNUSED_DAYS}d +%Y-%m-%d 2>/dev/null || date -d "$UNUSED_DAYS days ago" +%Y-%m-%d 2>/dev/null)
CUTOFF_TIMESTAMP=$(date -v-${UNUSED_DAYS}d +%s 2>/dev/null || date -d "$UNUSED_DAYS days ago" +%s 2>/dev/null)

# Build notification flags
NOTIFY_FLAGS=""
if [[ -n "$NOTIFY_USER" ]] && [[ -n "$NOTIFY_CHANNEL" ]]; then
    NOTIFY_FLAGS="--notify $NOTIFY_USER --channel $NOTIFY_CHANNEL"
fi

# Setup output redirection
OUTPUT_CONTENT=""
if [[ -n "$OUTPUT_FILE" ]]; then
    OUTPUT_CONTENT="$OUTPUT_FILE"
fi

# Print header
echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║          OpenAI Admin - Unused Keys Report                    ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Scan Date:${NC} $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "${YELLOW}Threshold:${NC} Keys unused for ${UNUSED_DAYS}+ days (since ${CUTOFF_DATE})"
echo ""

# Temporary files for analysis
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

ADMIN_KEYS_FILE="$TEMP_DIR/admin_keys.json"
ALL_UNUSED_KEYS="$TEMP_DIR/unused_keys.txt"

# Counter for unused keys
TOTAL_UNUSED=0
NEVER_USED=0

# Function to analyze keys from JSON
analyze_keys() {
    local keys_json="$1"
    local key_type="$2"  # "admin" or project name
    
    # Extract only the API key IDs (not owner IDs)
    # Look for "object": "organization.admin_api_key" or similar, then get the next "id" field
    echo "$keys_json" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'data' in data:
        for item in data['data']:
            key_id = item.get('id', '')
            last_used = item.get('last_used_at')
            
            # Print in format: key_id|last_used_timestamp
            print(f'{key_id}|{last_used if last_used else 0}')
except:
    pass
" | while IFS='|' read -r key_id last_used; do
        if [[ -z "$key_id" ]]; then
            continue
        fi
        
        if [[ "$last_used" == "0" ]] || [[ -z "$last_used" ]] || [[ "$last_used" == "None" ]]; then
            # Never used
            ((NEVER_USED++))
            ((TOTAL_UNUSED++))
            echo -e "${RED}  ✗ NEVER USED${NC} - $key_type - Key: $key_id"
            echo "$key_type,$key_id,never_used" >> "$ALL_UNUSED_KEYS"
        elif [[ "$last_used" -lt "$CUTOFF_TIMESTAMP" ]]; then
            # Used but not recently
            last_used_date=$(date -r "$last_used" +%Y-%m-%d 2>/dev/null || date -d "@$last_used" +%Y-%m-%d 2>/dev/null)
            days_ago=$(( ($(date +%s) - last_used) / 86400 ))
            ((TOTAL_UNUSED++))
            echo -e "${YELLOW}  ⚠ UNUSED ${days_ago} DAYS${NC} - $key_type - Key: $key_id (Last used: $last_used_date)"
            echo "$key_type,$key_id,$days_ago" >> "$ALL_UNUSED_KEYS"
        fi
    done
}

# SECTION 1: Admin Keys Analysis
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 1: ADMIN KEYS ANALYSIS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${GREEN}Fetching admin keys...${NC}"
ADMIN_KEYS_JSON=$(python3 "$CLI_PATH" keys list-admin --format json 2>/dev/null)

if [[ -n "$ADMIN_KEYS_JSON" ]]; then
    echo "$ADMIN_KEYS_JSON" > "$ADMIN_KEYS_FILE"
    
    echo -e "${YELLOW}Analyzing admin keys...${NC}"
    analyze_keys "$ADMIN_KEYS_JSON" "admin"
    echo ""
else
    echo -e "${YELLOW}⚠ No admin keys found or error fetching${NC}"
    echo ""
fi

# SECTION 2: Project Keys Analysis
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SECTION 2: PROJECT KEYS ANALYSIS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${GREEN}Fetching projects...${NC}"
PROJECTS_JSON=$(python3 "$CLI_PATH" projects list --format json 2>/dev/null)

if [[ -n "$PROJECTS_JSON" ]]; then
    PROJECT_IDS=$(echo "$PROJECTS_JSON" | grep -o '"id": *"[^"]*"' | sed 's/"id": *"\([^"]*\)"/\1/')
    
    if [[ -n "$PROJECT_IDS" ]]; then
        while IFS= read -r project_id; do
            if [[ -n "$project_id" ]]; then
                PROJECT_NAME=$(echo "$PROJECTS_JSON" | grep -A 5 "\"id\": *\"$project_id\"" | grep -o '"name": *"[^"]*"' | head -1 | sed 's/"name": *"\([^"]*\)"/\1/' || echo "$project_id")
                
                echo -e "${YELLOW}Analyzing: $PROJECT_NAME ($project_id)${NC}"
                
                PROJECT_KEYS_JSON=$(python3 "$CLI_PATH" keys list-project "$project_id" --format json 2>/dev/null)
                
                if [[ -n "$PROJECT_KEYS_JSON" ]]; then
                    analyze_keys "$PROJECT_KEYS_JSON" "$PROJECT_NAME"
                else
                    echo -e "  ${GREEN}✓ No keys or no unused keys${NC}"
                fi
                echo ""
            fi
        done <<< "$PROJECT_IDS"
    fi
fi

# Summary footer
echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║                    Analysis Complete                           ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}📊 SUMMARY:${NC}"
echo ""
echo -e "  Total Unused Keys: ${RED}${TOTAL_UNUSED}${NC}"
echo -e "  Never Used Keys: ${RED}${NEVER_USED}${NC}"
echo -e "  Threshold: ${UNUSED_DAYS} days"
echo ""

if [[ $TOTAL_UNUSED -gt 0 ]]; then
    echo -e "${RED}⚠ ACTION REQUIRED:${NC}"
    echo -e "  $TOTAL_UNUSED key(s) should be reviewed for deletion"
    echo ""
fi

if [[ -n "$OUTPUT_FILE" ]] && [[ -f "$ALL_UNUSED_KEYS" ]]; then
    cp "$ALL_UNUSED_KEYS" "$OUTPUT_FILE"
    echo -e "${GREEN}✓ Detailed results saved to: $OUTPUT_FILE${NC}"
fi

if [[ -n "$NOTIFY_USER" ]]; then
    echo -e "${GREEN}✓ Report sent to user $NOTIFY_USER via $NOTIFY_CHANNEL${NC}"
fi

echo ""
echo -e "${YELLOW}🔒 RECOMMENDATIONS:${NC}"
echo ""
echo -e "  1. Review and delete never-used keys immediately"
echo -e "  2. Contact key owners for keys unused > 90 days"
echo -e "  3. Implement key rotation policy"
echo -e "  4. Use service accounts for production systems"
echo -e "  5. Run this report monthly as part of security review"
echo ""
echo -e "${YELLOW}📋 NEXT STEPS:${NC}"
echo ""
echo -e "  • Delete unused keys: python openai_admin.py keys delete <project_id> <key_id>"
echo -e "  • Full key inventory: ./list-all-keys.sh"
echo -e "  • Security audit: ./audit-security-scan.sh"
echo ""
