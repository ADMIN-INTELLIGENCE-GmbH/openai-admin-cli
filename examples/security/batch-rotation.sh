#!/bin/bash
#
# Batch API Key Rotation Script
#
# This script processes all rotations defined in config/rotation.json
# using the two-step workflow with a grace period.
#
# Usage:
#   ./batch-rotation.sh create           # Day 1: Create all new keys (interactive)
#   ./batch-rotation.sh create --force   # Day 1: Create all new keys (automated)
#   ./batch-rotation.sh cleanup          # Day 7: Delete all old keys (interactive)
#   ./batch-rotation.sh cleanup --force  # Day 7: Delete all old keys (automated)
#
# Schedule with cron:
#   # First day of month at 9 AM - create new keys
#   0 9 1 * * /path/to/batch-rotation.sh create --force
#   
#   # Seventh day of month at 9 AM - cleanup old keys
#   0 9 7 * * /path/to/batch-rotation.sh cleanup --force
#

set -e

# Configuration
CONFIG_FILE="config/rotation.json"
FORCE_MODE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
ACTION=""
for arg in "$@"; do
    case $arg in
        create|cleanup)
            ACTION="$arg"
            ;;
        --force)
            FORCE_MODE=true
            ;;
        *)
            echo -e "${RED}Error: Unknown argument: $arg${NC}"
            echo "Usage: $0 [create|cleanup] [--force]"
            exit 1
            ;;
    esac
done

# Check if action was provided
if [ -z "$ACTION" ]; then
    echo -e "${RED}Error: No action specified${NC}"
    echo "Usage: $0 [create|cleanup] [--force]"
    echo ""
    echo "  create           Day 1: Create new keys (interactive)"
    echo "  create --force   Day 1: Create new keys (automated)"
    echo "  cleanup          Day 7: Delete old keys (interactive)"
    echo "  cleanup --force  Day 7: Delete old keys (automated)"
    echo ""
    echo "Use --force for automated/cron execution (skips confirmations)"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "cli.py" ]; then
    echo -e "${RED}Error: cli.py not found${NC}"
    echo "Please run this script from the openai-helper directory"
    exit 1
fi

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Config file not found: $CONFIG_FILE${NC}"
    echo ""
    echo "Create it from the example:"
    echo "  cp config/rotation.json.example config/rotation.json"
    echo "  # Edit config/rotation.json with your projects and keys"
    exit 1
fi

# Show what will be done
echo -e "${BLUE}==================================================================${NC}"
echo -e "${BLUE}Batch API Key Rotation - $(echo $ACTION | tr '[:lower:]' '[:upper:]')${NC}"
echo -e "${BLUE}==================================================================${NC}"
echo ""
echo -e "Config File: ${GREEN}$CONFIG_FILE${NC}"
echo -e "Action:      ${GREEN}$ACTION${NC}"
echo ""

# Count projects and keys
PROJECTS=$(jq '.rotations | length' "$CONFIG_FILE" 2>/dev/null || echo "0")
TOTAL_KEYS=$(jq '[.rotations[].keys | length] | add' "$CONFIG_FILE" 2>/dev/null || echo "0")

if [ "$PROJECTS" == "0" ] || [ "$TOTAL_KEYS" == "0" ]; then
    echo -e "${RED}Error: No rotations found in config file${NC}"
    echo "Check your config file structure"
    exit 1
fi

echo "Projects:    $PROJECTS"
echo "Total Keys:  $TOTAL_KEYS"
echo ""

if [ "$FORCE_MODE" = true ]; then
    echo -e "${YELLOW}Running in FORCE mode (automated)${NC}"
    echo ""
fi

if [ "$ACTION" == "create" ]; then
    echo -e "${GREEN}==================================================================${NC}"
    echo -e "${GREEN}STEP 1: CREATE NEW API KEYS${NC}"
    echo -e "${GREEN}==================================================================${NC}"
    echo ""
    echo "This will create new API keys for all configured rotations."
    echo "Old keys will remain active during the grace period."
    echo ""
    echo "After this step:"
    echo "  1. Check Mattermost for new API key values"
    echo "  2. Update all application configurations"
    echo "  3. Test thoroughly in staging/production"
    echo "  4. Wait for grace period (7 days recommended)"
    echo "  5. Run: $0 cleanup"
    echo ""
    
    # Dry run first
    echo -e "${YELLOW}Preview:${NC}"
    python3 cli.py rotation batch \
        --config-file "$CONFIG_FILE" \
        --action create \
        --dry-run
    
    echo ""
    
    if [ "$FORCE_MODE" = false ]; then
        read -p "Continue with creating new keys? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Cancelled."
            exit 0
        fi
    else
        echo -e "${GREEN}Proceeding automatically (--force mode)${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}Creating new keys...${NC}"
    python3 cli.py rotation batch \
        --config-file "$CONFIG_FILE" \
        --action create \
        --force
    
    echo ""
    echo -e "${YELLOW}==================================================================${NC}"
    echo -e "${YELLOW}NEXT STEPS:${NC}"
    echo -e "${YELLOW}==================================================================${NC}"
    echo "1. Check Mattermost notifications for new API keys"
    echo "2. Update application configurations with new keys"
    echo "3. Deploy and test thoroughly"
    echo "4. After grace period (e.g., 7 days), run:"
    echo "   $0 cleanup"
    echo -e "${YELLOW}==================================================================${NC}"

elif [ "$ACTION" == "cleanup" ]; then
    echo -e "${GREEN}==================================================================${NC}"
    echo -e "${GREEN}STEP 2: CLEANUP OLD API KEYS${NC}"
    echo -e "${GREEN}==================================================================${NC}"
    echo ""
    echo "This will DELETE old API keys for all configured rotations."
    echo ""
    echo -e "${YELLOW}WARNING: Make sure all applications are using the new keys!${NC}"
    echo ""
    
    # Dry run first
    echo -e "${YELLOW}Preview of what will be deleted:${NC}"
    echo ""
    python3 cli.py rotation batch \
        --config-file "$CONFIG_FILE" \
        --action cleanup \
        --dry-run
    
    echo ""
    
    if [ "$FORCE_MODE" = false ]; then
        echo -e "${RED}WARNING: This will permanently delete old API keys!${NC}"
        read -p "Are you SURE you want to delete these keys? Type 'yes' to confirm: " -r
        echo
        if [[ ! $REPLY == "yes" ]]; then
            echo "Cancelled."
            exit 0
        fi
    else
        echo -e "${GREEN}Proceeding automatically (--force mode)${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}Deleting old keys...${NC}"
    python3 cli.py rotation batch \
        --config-file "$CONFIG_FILE" \
        --action cleanup \
        --force
    
    echo ""
    echo -e "${GREEN}==================================================================${NC}"
    echo -e "${GREEN}CLEANUP COMPLETE!${NC}"
    echo -e "${GREEN}==================================================================${NC}"
    echo "Old keys have been deleted."
    echo "Your rotation cycle is complete."
    echo -e "${GREEN}==================================================================${NC}"
fi

echo ""
echo -e "${BLUE}Done!${NC}"
