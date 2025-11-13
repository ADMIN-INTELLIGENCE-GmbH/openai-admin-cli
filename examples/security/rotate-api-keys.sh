#!/bin/bash
#
# API Key Rotation Script
# Rotates API keys for OpenAI projects using date-based service account naming
#
# Usage:
#   ./rotate-api-keys.sh [--dry-run] [--project-id PROJECT_ID] [--prefix PREFIX] [--notify-user USER_ID]
#
# Environment Variables:
#   OPENAI_ADMIN_KEY - Required: Your OpenAI admin API key
#   ROTATION_PROJECT_ID - Optional: Default project ID
#   ROTATION_PREFIX - Optional: Default naming prefix (default: api-key)
#   ROTATION_NOTIFY_USER - Optional: Default user ID to notify
#
# Examples:
#   # Perform rotation with interactive prompts
#   ./rotate-api-keys.sh
#
#   # Dry run to see what would happen
#   ./rotate-api-keys.sh --dry-run
#
#   # Rotate keys for specific project
#   ./rotate-api-keys.sh --project-id proj_abc123xyz --prefix deployment-key
#
#   # Rotate and notify user
#   ./rotate-api-keys.sh --project-id proj_abc123xyz --notify-user 1
#
# This script will:
# 1. Create a new service account named: <prefix>-YYYY-MM-DD
# 2. Generate a new API key for the service account
# 3. Delete older service accounts with the same prefix (keeps newest + new one)
# 4. Optionally send the new API key to a user via Mattermost

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DRY_RUN=""
PROJECT_ID="${ROTATION_PROJECT_ID:-}"
PREFIX="${ROTATION_PREFIX:-api-key}"
NOTIFY_USER="${ROTATION_NOTIFY_USER:-}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --project-id)
            PROJECT_ID="$2"
            shift 2
            ;;
        --prefix)
            PREFIX="$2"
            shift 2
            ;;
        --notify-user)
            NOTIFY_USER="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [--project-id PROJECT_ID] [--prefix PREFIX] [--notify-user USER_ID]"
            echo ""
            echo "Options:"
            echo "  --dry-run            Show what would be done without making changes"
            echo "  --project-id ID      OpenAI project ID"
            echo "  --prefix PREFIX      Service account naming prefix (default: api-key)"
            echo "  --notify-user ID     User ID to notify via Mattermost"
            echo "  -h, --help           Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            exit 1
            ;;
    esac
done

# Check required environment variable
if [ -z "$OPENAI_ADMIN_KEY" ]; then
    echo -e "${RED}Error: OPENAI_ADMIN_KEY environment variable is required${NC}"
    echo "Set it with: export OPENAI_ADMIN_KEY='your-admin-key'"
    exit 1
fi

# Interactive prompts if values not provided
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Project ID not specified.${NC}"
    read -p "Enter OpenAI Project ID: " PROJECT_ID
    
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}Error: Project ID is required${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}API Key Rotation${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Project ID:    ${GREEN}$PROJECT_ID${NC}"
echo -e "Prefix:        ${GREEN}$PREFIX${NC}"
echo -e "Notify User:   ${GREEN}${NOTIFY_USER:-None}${NC}"
echo -e "Dry Run:       ${GREEN}${DRY_RUN:-No}${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Confirm if not dry run
if [ -z "$DRY_RUN" ]; then
    read -p "Proceed with rotation? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Cancelled.${NC}"
        exit 0
    fi
fi

# Build command
CMD="python cli.py rotation execute --project-id $PROJECT_ID --prefix $PREFIX"

if [ -n "$NOTIFY_USER" ]; then
    CMD="$CMD --notify-user $NOTIFY_USER"
fi

if [ -n "$DRY_RUN" ]; then
    CMD="$CMD $DRY_RUN"
fi

# Execute rotation
echo -e "${BLUE}Executing rotation...${NC}"
echo ""

if $CMD; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Rotation completed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    if [ -z "$DRY_RUN" ]; then
        echo ""
        echo -e "${YELLOW}Next Steps:${NC}"
        echo "1. Update your application configuration with the new API key"
        echo "2. Test the new API key in a staging environment"
        echo "3. Deploy the updated configuration to production"
        echo "4. Monitor for any authentication errors"
    fi
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Rotation failed!${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
