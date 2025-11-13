#!/bin/bash
#
# Two-Step API Key Rotation Script
#
# This script demonstrates the recommended two-step rotation workflow:
#   Day 1:  Create new key (this script with --create)
#   Day 7:  Cleanup old keys (this script with --cleanup)
#
# This allows a grace period for migrating your application to the new key.
#
# Usage:
#   ./two-step-rotation.sh --create   # Day 1: Create new key
#   ./two-step-rotation.sh --cleanup  # Day 7: Delete old keys
#

set -e

# Configuration - EDIT THESE VALUES
PROJECT_ID="proj_01srJH5HJkvZfbFbaEwhzHaE"  # Your OpenAI project ID
PREFIX="inventory-server"                    # Your naming prefix
NOTIFY_USER="49"                             # Mattermost user ID to notify
DATE_FORMAT="YY-MM"                          # Date format: YY-MM or YYYY-MM-DD
KEEP_LATEST=1                                # Number of keys to keep during cleanup

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ "$1" != "--create" ] && [ "$1" != "--cleanup" ]; then
    echo -e "${RED}Error: Invalid argument${NC}"
    echo "Usage: $0 [--create|--cleanup]"
    echo ""
    echo "  --create   Step 1: Create new key (run on Day 1)"
    echo "  --cleanup  Step 2: Delete old keys (run on Day 7)"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "cli.py" ]; then
    echo -e "${RED}Error: cli.py not found${NC}"
    echo "Please run this script from the openai-helper directory"
    exit 1
fi

if [ "$1" == "--create" ]; then
    echo -e "${GREEN}==================================================================${NC}"
    echo -e "${GREEN}STEP 1: CREATE NEW API KEY${NC}"
    echo -e "${GREEN}==================================================================${NC}"
    echo ""
    echo "This will create a new API key while keeping old ones active."
    echo "After this step:"
    echo "  1. Save the new API key value"
    echo "  2. Update your application configuration"
    echo "  3. Test thoroughly in staging/production"
    echo "  4. Wait for your grace period (e.g., 7 days)"
    echo "  5. Run: $0 --cleanup"
    echo ""
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
    
    echo ""
    python3 cli.py rotation create \
        --project-id "$PROJECT_ID" \
        --prefix "$PREFIX" \
        --date-format "$DATE_FORMAT" \
        --notify-user "$NOTIFY_USER" \
        --force
    
    echo ""
    echo -e "${YELLOW}==================================================================${NC}"
    echo -e "${YELLOW}NEXT STEPS:${NC}"
    echo -e "${YELLOW}==================================================================${NC}"
    echo "1. Save the API key value shown above in a secure location"
    echo "2. Update your application's configuration with the new key"
    echo "3. Deploy and test thoroughly"
    echo "4. After 7 days (or your chosen grace period), run:"
    echo "   $0 --cleanup"
    echo -e "${YELLOW}==================================================================${NC}"
    
elif [ "$1" == "--cleanup" ]; then
    echo -e "${GREEN}==================================================================${NC}"
    echo -e "${GREEN}STEP 2: CLEANUP OLD API KEYS${NC}"
    echo -e "${GREEN}==================================================================${NC}"
    echo ""
    echo "This will DELETE old API keys, keeping only the latest $KEEP_LATEST."
    echo ""
    echo -e "${YELLOW}WARNING: Make sure your application is using the new key!${NC}"
    echo ""
    
    # Show current keys
    echo "Current keys:"
    python3 cli.py rotation list "$PROJECT_ID" --prefix "$PREFIX"
    echo ""
    
    # Dry run first
    echo "Preview of what will be deleted:"
    echo ""
    python3 cli.py rotation cleanup \
        --project-id "$PROJECT_ID" \
        --prefix "$PREFIX" \
        --keep-latest "$KEEP_LATEST" \
        --dry-run
    
    echo ""
    read -p "Are you SURE you want to delete these keys? (yes/N) " -r
    echo
    if [[ ! $REPLY =~ ^yes$ ]]; then
        echo "Cancelled."
        exit 0
    fi
    
    echo ""
    python3 cli.py rotation cleanup \
        --project-id "$PROJECT_ID" \
        --prefix "$PREFIX" \
        --keep-latest "$KEEP_LATEST" \
        --force
    
    echo ""
    echo -e "${GREEN}==================================================================${NC}"
    echo -e "${GREEN}CLEANUP COMPLETE!${NC}"
    echo -e "${GREEN}==================================================================${NC}"
    echo "Old keys have been deleted."
    echo "Your rotation cycle is complete."
    echo -e "${GREEN}==================================================================${NC}"
fi
