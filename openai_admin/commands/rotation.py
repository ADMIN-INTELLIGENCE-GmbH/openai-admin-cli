"""Key rotation commands"""
import click
import json
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from tabulate import tabulate
from openai_admin.utils import format_timestamp, with_notification, notification_options


@click.group()
def rotation():
    """Manage API key rotation"""
    pass


def _load_rotation_config() -> Dict[str, Any]:
    """Load rotation configuration from config file"""
    config_path = Path(__file__).parent.parent.parent / 'config' / 'rotation.json'
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        click.echo(f"[ERROR] Failed to load rotation config: {e}", err=True)
        return {}


def _parse_service_account_date(name: str, prefix: str) -> Optional[datetime]:
    """Extract date from service account name
    
    Supports multiple date formats:
    - YYYY-MM-DD (e.g., 'api-key-2024-11-13')
    - YY-MM (e.g., 'chatbot-server-24-11')
    
    Args:
        name: Service account name (e.g., 'api-key-2024-11-13' or 'chatbot-server-24-11')
        prefix: Expected prefix (e.g., 'api-key' or 'chatbot-server')
    
    Returns:
        datetime object if date found, None otherwise
    """
    # Try full date format first: prefix-YYYY-MM-DD
    pattern_full = rf'^{re.escape(prefix)}-(\d{{4}})-(\d{{2}})-(\d{{2}})$'
    match = re.match(pattern_full, name)
    
    if match:
        year, month, day = match.groups()
        try:
            return datetime(int(year), int(month), int(day))
        except ValueError:
            return None
    
    # Try short date format: prefix-YY-MM (assume first day of month)
    pattern_short = rf'^{re.escape(prefix)}-(\d{{2}})-(\d{{2}})$'
    match = re.match(pattern_short, name)
    
    if match:
        year_short, month = match.groups()
        try:
            # Convert YY to YYYY (assume 2000s)
            year = 2000 + int(year_short)
            # Use first day of the month for comparison
            return datetime(year, int(month), 1)
        except ValueError:
            return None
    
    return None


def _find_matching_service_accounts(service_accounts: List[Dict], prefix: str) -> List[Dict]:
    """Find service accounts matching the naming pattern
    
    Args:
        service_accounts: List of service account objects
        prefix: Naming prefix to match
    
    Returns:
        List of matching service accounts with parsed dates and actual creation timestamps
    """
    matching = []
    
    for sa in service_accounts:
        name = sa.get('name', '')
        date = _parse_service_account_date(name, prefix)
        
        if date:
            matching.append({
                'id': sa.get('id'),
                'name': name,
                'date': date,  # Parsed date from name (for sorting)
                'created_at': sa.get('created_at'),  # Actual creation timestamp
                'role': sa.get('role')
            })
    
    # Sort by date descending (newest first)
    matching.sort(key=lambda x: x['date'], reverse=True)
    
    return matching


@rotation.command('create')
@click.option('--config-file', type=click.Path(exists=True), help='Path to rotation configuration file')
@click.option('--project-id', help='Project ID (overrides config file)')
@click.option('--prefix', help='Service account naming prefix (e.g., inventory-server)')
@click.option('--date-format', type=click.Choice(['YYYY-MM-DD', 'YY-MM']), default='YY-MM', help='Date format for service account names (default: YY-MM)')
@click.option('--notify-user', help='User ID to notify via Mattermost (from users.json)')
@click.option('--dry-run', is_flag=True, help='Show what would be done without making changes')
@click.option('--force', is_flag=True, help='Skip confirmation prompts')
@click.pass_context
def create_rotation_key(ctx, config_file, project_id, prefix, date_format, notify_user, dry_run, force):
    """Create a new rotation key without deleting old ones
    
    This is Step 1 of a two-step rotation process:
    1. Create new key (this command) - allows both keys to be active
    2. Cleanup old keys (use 'rotation cleanup') - after updating your application
    
    Date Formats:
      - YY-MM: Short format (e.g., 'inventory-server-24-11') [DEFAULT]
      - YYYY-MM-DD: Full format (e.g., 'api-key-2024-11-13')
    
    Example workflow:
        # Day 1: Create new key
        python3 cli.py rotation create --project-id proj_123 --prefix inventory-server --notify-user 49
        
        # Update your application with the new key
        # Test thoroughly
        
        # Day 7: Cleanup old keys
        python3 cli.py rotation cleanup --project-id proj_123 --prefix inventory-server
    """
    client = ctx.obj['client']
    
    # Load configuration
    if config_file:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except Exception as e:
            click.echo(f"[ERROR] Failed to load config file: {e}", err=True)
            sys.exit(1)
    else:
        config = _load_rotation_config()
    
    # Override with command-line arguments
    if project_id:
        config['project_id'] = project_id
    if prefix:
        config['prefix'] = prefix
    if notify_user:
        config['notify_user'] = notify_user
    if date_format:
        config['date_format'] = date_format
    
    # Validate required parameters
    if not config.get('project_id'):
        click.echo("[ERROR] Project ID is required (use --project-id or config file)", err=True)
        sys.exit(1)
    
    if not config.get('prefix'):
        click.echo("[ERROR] Service account prefix is required (use --prefix or config file)", err=True)
        sys.exit(1)
    
    project_id = config['project_id']
    sa_prefix = config['prefix']
    notify_user_id = config.get('notify_user')
    date_fmt = config.get('date_format', 'YY-MM')
    
    indent_1 = ' ' * 3
    
    # Show configuration
    click.echo(f"\n{'='*80}")
    click.echo(f"Create New Rotation Key")
    click.echo(f"{'='*80}")
    click.echo(f"Project ID:       {project_id}")
    click.echo(f"Naming Prefix:    {sa_prefix}")
    click.echo(f"Date Format:      {date_fmt}")
    click.echo(f"Notify User:      {notify_user_id or 'None'}")
    click.echo(f"Dry Run:          {dry_run}")
    click.echo(f"{'='*80}\n")
    
    # Step 1: List existing service accounts
    click.echo("[STEP 1] Fetching existing service accounts...")
    try:
        result = client.list_project_service_accounts(project_id, limit=100)
        all_service_accounts = result.get('data', [])
    except Exception as e:
        click.echo(f"[ERROR] Failed to fetch service accounts: {e}", err=True)
        sys.exit(1)
    
    # Find matching service accounts
    matching_accounts = _find_matching_service_accounts(all_service_accounts, sa_prefix)
    
    click.echo(f"{indent_1}Total service accounts: {len(all_service_accounts)}")
    click.echo(f"{indent_1}Matching pattern '{sa_prefix}-<date>': {len(matching_accounts)}")
    
    if matching_accounts:
        click.echo(f"\n{indent_1}Existing service accounts (will remain active):")
        for sa in matching_accounts:
            click.echo(f"{indent_1*2}- {sa['name']} (ID: {sa['id']}, Date: {sa['date'].strftime('%Y-%m-%d')})")
    
    # Step 2: Create new service account
    today = datetime.now()
    
    # Generate name based on date format
    if date_fmt == 'YY-MM':
        new_sa_name = f"{sa_prefix}-{today.strftime('%y-%m')}"
    else:  # YYYY-MM-DD
        new_sa_name = f"{sa_prefix}-{today.strftime('%Y-%m-%d')}"
    
    click.echo(f"\n[STEP 2] Creating new service account: {new_sa_name}")
    
    if dry_run:
        click.echo(f"{indent_1}[DRY RUN] Would create service account '{new_sa_name}'")
        new_api_key_value = "sk-proj-dummy-key-for-dry-run"
        new_sa_id = "sa_dummy_id"
    else:
        try:
            create_result = client.create_project_service_account(project_id, new_sa_name)
            new_sa_id = create_result.get('id')
            
            click.echo(f"{indent_1}[SUCCESS] Created service account '{new_sa_name}'")
            click.echo(f"{indent_1}Service Account ID: {new_sa_id}")
            
            # Extract API key
            api_key = create_result.get('api_key', {})
            new_api_key_value = api_key.get('value')
            new_api_key_id = api_key.get('id')
            
            if new_api_key_value:
                click.echo(f"{indent_1}API Key ID: {new_api_key_id}")
                click.echo(f"\n{indent_1}{'='*70}")
                click.echo(f"{indent_1}[WARNING] NEW API KEY (SAVE THIS NOW!)")
                click.echo(f"{indent_1}{'='*70}")
                click.echo(f"{indent_1}Key Value: {new_api_key_value}")
                click.echo(f"{indent_1}{'='*70}\n")
            else:
                click.echo(f"{indent_1}[WARNING] No API key returned in response")
                new_api_key_value = None
        except Exception as e:
            click.echo(f"{indent_1}[ERROR] Failed to create service account: {e}", err=True)
            sys.exit(1)
    
    # Step 3: Send notification if configured
    if notify_user_id and new_api_key_value:
        click.echo(f"\n[STEP 3] Sending notification to user {notify_user_id}...")
        
        if dry_run:
            click.echo(f"{indent_1}[DRY RUN] Would send Mattermost notification")
        else:
            try:
                from openai_admin.notifier import MattermostNotifier
                
                notifier = MattermostNotifier()
                
                # Format message
                message = f"""🔑 **New OpenAI API Key Created**

**Project ID:** `{project_id}`
**Service Account:** `{new_sa_name}`
**Service Account ID:** `{new_sa_id}`

**New API Key:**
```
{new_api_key_value}
```

⚠️ **Important:** 
- Save this API key immediately in a secure location
- Both old and new keys are currently active
- Update your application configuration
- Test thoroughly before running cleanup

**Next Steps:**
1. Update application configuration with new API key
2. Deploy and test in staging/production
3. After 7 days (or your grace period), run cleanup:
   `python3 cli.py rotation cleanup --project-id {project_id} --prefix {sa_prefix}`

**Current Active Keys:** {len(matching_accounts) + 1}
"""
                
                notifier.send_to_user(notify_user_id, message)
                click.echo(f"{indent_1}[SUCCESS] Notification sent via Mattermost")
                
            except Exception as e:
                click.echo(f"{indent_1}[ERROR] Failed to send notification: {e}", err=True)
                click.echo(f"{indent_1}[WARNING] Key created but notification failed")
    elif notify_user_id and not new_api_key_value:
        click.echo(f"\n[STEP 3] Skipping notification (no API key to send)")
    else:
        click.echo(f"\n[STEP 3] No notification configured")
    
    # Summary
    click.echo(f"\n{'='*80}")
    click.echo(f"Summary")
    click.echo(f"{'='*80}")
    click.echo(f"Created:         {new_sa_name}")
    click.echo(f"Active Keys:     {len(matching_accounts) + 1} (old keys still active)")
    click.echo(f"Notification:    {'Sent' if notify_user_id and new_api_key_value and not dry_run else 'Skipped'}")
    click.echo(f"Status:          {'DRY RUN - No changes made' if dry_run else 'SUCCESS'}")
    click.echo(f"\n[TIP] After updating your application, cleanup old keys with:")
    click.echo(f"{indent_1}python3 cli.py rotation cleanup --project-id {project_id} --prefix {sa_prefix}")
    click.echo(f"{'='*80}\n")


@rotation.command('cleanup')
@click.option('--config-file', type=click.Path(exists=True), help='Path to rotation configuration file')
@click.option('--project-id', help='Project ID (overrides config file)')
@click.option('--prefix', help='Service account naming prefix (e.g., inventory-server)')
@click.option('--keep-latest', default=1, type=int, help='Number of latest keys to keep (default: 1)')
@click.option('--dry-run', is_flag=True, help='Show what would be deleted without making changes')
@click.option('--force', is_flag=True, help='Skip confirmation prompts')
@click.pass_context
def cleanup_old_keys(ctx, config_file, project_id, prefix, keep_latest, dry_run, force):
    """Cleanup old rotation keys, keeping only the newest ones
    
    This is Step 2 of the rotation process. Run this after you've:
    1. Created a new key with 'rotation create'
    2. Updated your application with the new key
    3. Tested thoroughly in production
    
    Examples:
        # Keep only the newest key (delete all others)
        python3 cli.py rotation cleanup --project-id proj_123 --prefix inventory-server
        
        # Keep 2 newest keys (useful for extra safety)
        python3 cli.py rotation cleanup --project-id proj_123 --prefix inventory-server --keep-latest 2
        
        # Preview what would be deleted
        python3 cli.py rotation cleanup --project-id proj_123 --prefix inventory-server --dry-run
    """
    client = ctx.obj['client']
    
    # Load configuration
    if config_file:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except Exception as e:
            click.echo(f"[ERROR] Failed to load config file: {e}", err=True)
            sys.exit(1)
    else:
        config = _load_rotation_config()
    
    # Override with command-line arguments
    if project_id:
        config['project_id'] = project_id
    if prefix:
        config['prefix'] = prefix
    
    # Validate required parameters
    if not config.get('project_id'):
        click.echo("[ERROR] Project ID is required (use --project-id or config file)", err=True)
        sys.exit(1)
    
    if not config.get('prefix'):
        click.echo("[ERROR] Service account prefix is required (use --prefix or config file)", err=True)
        sys.exit(1)
    
    project_id = config['project_id']
    sa_prefix = config['prefix']
    
    indent_1 = ' ' * 3
    
    # Show configuration
    click.echo(f"\n{'='*80}")
    click.echo(f"Cleanup Old Rotation Keys")
    click.echo(f"{'='*80}")
    click.echo(f"Project ID:       {project_id}")
    click.echo(f"Naming Prefix:    {sa_prefix}")
    click.echo(f"Keep Latest:      {keep_latest}")
    click.echo(f"Dry Run:          {dry_run}")
    click.echo(f"{'='*80}\n")
    
    # Fetch existing service accounts
    click.echo("[STEP 1] Fetching existing service accounts...")
    try:
        result = client.list_project_service_accounts(project_id, limit=100)
        all_service_accounts = result.get('data', [])
    except Exception as e:
        click.echo(f"[ERROR] Failed to fetch service accounts: {e}", err=True)
        sys.exit(1)
    
    # Find matching service accounts
    matching_accounts = _find_matching_service_accounts(all_service_accounts, sa_prefix)
    
    click.echo(f"{indent_1}Total service accounts: {len(all_service_accounts)}")
    click.echo(f"{indent_1}Matching pattern '{sa_prefix}-<date>': {len(matching_accounts)}")
    
    if not matching_accounts:
        click.echo(f"\n[INFO] No service accounts found matching pattern '{sa_prefix}-<date>'")
        return
    
    if len(matching_accounts) <= keep_latest:
        click.echo(f"\n[INFO] Only {len(matching_accounts)} key(s) found. Nothing to cleanup.")
        click.echo(f"{indent_1}All keys are being kept (keep-latest={keep_latest})")
        return
    
    # Determine which to keep and which to delete
    keys_to_keep = matching_accounts[:keep_latest]
    keys_to_delete = matching_accounts[keep_latest:]
    
    click.echo(f"\n{indent_1}Keys to KEEP ({len(keys_to_keep)}):")
    for sa in keys_to_keep:
        created_datetime = datetime.fromtimestamp(sa['created_at'])
        age_days = (datetime.now() - created_datetime).days
        click.echo(f"{indent_1*2}✓ {sa['name']} (Age: {age_days} days, Created: {format_timestamp(sa['created_at'])})")
    
    click.echo(f"\n{indent_1}Keys to DELETE ({len(keys_to_delete)}):")
    for sa in keys_to_delete:
        created_datetime = datetime.fromtimestamp(sa['created_at'])
        age_days = (datetime.now() - created_datetime).days
        click.echo(f"{indent_1*2}✗ {sa['name']} (Age: {age_days} days, Created: {format_timestamp(sa['created_at'])})")
    
    # Confirm deletion
    if not dry_run and not force:
        click.echo(f"\n[WARNING] This will delete {len(keys_to_delete)} service account(s) and their API keys.")
        click.echo(f"{indent_1}This action cannot be undone!")
        if not click.confirm('\nDo you want to continue?'):
            click.echo("Cancelled.")
            return
    
    # Delete old keys
    click.echo(f"\n[STEP 2] Deleting {len(keys_to_delete)} old service account(s)...")
    
    deleted_count = 0
    for sa in keys_to_delete:
        click.echo(f"{indent_1}Deleting '{sa['name']}' (ID: {sa['id']})...")
        
        if dry_run:
            click.echo(f"{indent_1*2}[DRY RUN] Would delete service account")
            deleted_count += 1
        else:
            try:
                client.delete_project_service_account(project_id, sa['id'])
                click.echo(f"{indent_1*2}[SUCCESS] Deleted successfully")
                deleted_count += 1
            except Exception as e:
                click.echo(f"{indent_1*2}[ERROR] Failed to delete: {e}", err=True)
    
    # Summary
    click.echo(f"\n{'='*80}")
    click.echo(f"Cleanup Summary")
    click.echo(f"{'='*80}")
    click.echo(f"Kept:            {len(keys_to_keep)} service account(s)")
    click.echo(f"Deleted:         {deleted_count} service account(s)")
    click.echo(f"Status:          {'DRY RUN - No changes made' if dry_run else 'SUCCESS'}")
    click.echo(f"{'='*80}\n")


@rotation.command('execute')
@click.option('--config-file', type=click.Path(exists=True), help='Path to rotation configuration file')
@click.option('--project-id', help='Project ID (overrides config file)')
@click.option('--prefix', help='Service account naming prefix (e.g., api-key)')
@click.option('--date-format', type=click.Choice(['YYYY-MM-DD', 'YY-MM']), default='YY-MM', help='Date format for service account names (default: YY-MM)')
@click.option('--notify-user', help='User ID to notify via Mattermost (from users.json)')
@click.option('--dry-run', is_flag=True, help='Show what would be done without making changes')
@click.option('--force', is_flag=True, help='Skip confirmation prompts')
@click.pass_context
def execute_rotation(ctx, config_file, project_id, prefix, date_format, notify_user, dry_run, force):
    """Execute IMMEDIATE API key rotation (create + delete in one step)
    
    ⚠️  WARNING: This creates a new key and immediately deletes old ones.
    
    For safer rotation with a grace period, use the two-step process instead:
      1. python3 cli.py rotation create   (creates new key, keeps old ones)
      2. python3 cli.py rotation cleanup  (deletes old keys after migration)
    
    Date Formats:
      - YY-MM: Short format (e.g., 'api-key-24-11' for November 2024) [DEFAULT]
      - YYYY-MM-DD: Full format (e.g., 'api-key-2024-11-13')
    
    Example:
        python3 cli.py rotation execute --project-id proj_123 --prefix prod-api
    """
    client = ctx.obj['client']
    
    # Load configuration
    if config_file:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except Exception as e:
            click.echo(f"[ERROR] Failed to load config file: {e}", err=True)
            sys.exit(1)
    else:
        config = _load_rotation_config()
    
    # Override with command-line arguments
    if project_id:
        config['project_id'] = project_id
    if prefix:
        config['prefix'] = prefix
    if notify_user:
        config['notify_user'] = notify_user
    if date_format:
        config['date_format'] = date_format
    
    # Validate required parameters
    if not config.get('project_id'):
        click.echo("[ERROR] Project ID is required (use --project-id or config file)", err=True)
        sys.exit(1)
    
    if not config.get('prefix'):
        click.echo("[ERROR] Service account prefix is required (use --prefix or config file)", err=True)
        sys.exit(1)
    
    project_id = config['project_id']
    sa_prefix = config['prefix']
    notify_user_id = config.get('notify_user')
    date_fmt = config.get('date_format', 'YY-MM')  # Default to YY-MM
    
    indent_1 = ' ' * 3
    
    # Show configuration
    click.echo(f"\n{'='*80}")
    click.echo(f"API Key Rotation Configuration")
    click.echo(f"{'='*80}")
    click.echo(f"Project ID:       {project_id}")
    click.echo(f"Naming Prefix:    {sa_prefix}")
    click.echo(f"Date Format:      {date_fmt}")
    click.echo(f"Notify User:      {notify_user_id or 'None'}")
    click.echo(f"Dry Run:          {dry_run}")
    click.echo(f"{'='*80}\n")
    
    # Step 1: List existing service accounts
    click.echo("[STEP 1] Fetching existing service accounts...")
    try:
        result = client.list_project_service_accounts(project_id, limit=100)
        all_service_accounts = result.get('data', [])
    except Exception as e:
        click.echo(f"[ERROR] Failed to fetch service accounts: {e}", err=True)
        sys.exit(1)
    
    # Find matching service accounts
    matching_accounts = _find_matching_service_accounts(all_service_accounts, sa_prefix)
    
    click.echo(f"{indent_1}Total service accounts: {len(all_service_accounts)}")
    click.echo(f"{indent_1}Matching pattern '{sa_prefix}-<date>': {len(matching_accounts)}")
    
    if matching_accounts:
        click.echo(f"\n{indent_1}Existing service accounts:")
        for sa in matching_accounts:
            click.echo(f"{indent_1*2}- {sa['name']} (ID: {sa['id']}, Date: {sa['date'].strftime('%Y-%m-%d')})")
    
    # Step 2: Create new service account
    today = datetime.now()
    
    # Generate name based on date format
    if date_fmt == 'YY-MM':
        new_sa_name = f"{sa_prefix}-{today.strftime('%y-%m')}"
    else:  # YYYY-MM-DD
        new_sa_name = f"{sa_prefix}-{today.strftime('%Y-%m-%d')}"
    
    # Check if service account for current period already exists
    current_sa_exists = any(sa['name'] == new_sa_name for sa in matching_accounts)
    
    if current_sa_exists:
        click.echo(f"\n[STEP 2] Service account '{new_sa_name}' already exists - skipping creation")
        new_api_key_value = None
        new_sa_id = None
    else:
        click.echo(f"\n[STEP 2] Creating new service account: {new_sa_name}")
    if current_sa_exists:
        click.echo(f"\n[STEP 2] Service account '{new_sa_name}' already exists - skipping creation")
        new_api_key_value = None
        new_sa_id = None
    else:
        click.echo(f"\n[STEP 2] Creating new service account: {new_sa_name}")
    
        if dry_run:
            click.echo(f"{indent_1}[DRY RUN] Would create service account '{new_sa_name}'")
            new_api_key_value = "sk-proj-dummy-key-for-dry-run"
            new_sa_id = "sa_dummy_id"
        else:
            try:
                create_result = client.create_project_service_account(project_id, new_sa_name)
                new_sa_id = create_result.get('id')
                
                click.echo(f"{indent_1}[SUCCESS] Created service account '{new_sa_name}'")
                click.echo(f"{indent_1}Service Account ID: {new_sa_id}")
                
                # Extract API key
                api_key = create_result.get('api_key', {})
                new_api_key_value = api_key.get('value')
                new_api_key_id = api_key.get('id')
                
                if new_api_key_value:
                    click.echo(f"{indent_1}API Key ID: {new_api_key_id}")
                    click.echo(f"\n{indent_1}{'='*70}")
                    click.echo(f"{indent_1}[WARNING] NEW API KEY (SAVE THIS NOW!)")
                    click.echo(f"{indent_1}{'='*70}")
                    click.echo(f"{indent_1}Key Value: {new_api_key_value}")
                    click.echo(f"{indent_1}{'='*70}\n")
                else:
                    click.echo(f"{indent_1}[WARNING] No API key returned in response")
                    new_api_key_value = None
            except Exception as e:
                click.echo(f"{indent_1}[ERROR] Failed to create service account: {e}", err=True)
                sys.exit(1)
    
    # Step 3: Delete old service accounts (keep only the newest existing one + new one)
    accounts_to_delete = []
    
    # Delete all but the most recent existing one
    if len(matching_accounts) >= 2:
        # Keep newest, delete the rest
        accounts_to_delete = matching_accounts[1:]
    elif len(matching_accounts) == 1:
        # Check if the existing one is older than today
        existing_date = matching_accounts[0]['date'].date()
        today_date = today.date()
        
        if existing_date < today_date:
            # New one is for today, delete old one
            accounts_to_delete = matching_accounts
    
    if accounts_to_delete:
        click.echo(f"\n[STEP 3] Deleting {len(accounts_to_delete)} old service account(s)...")
        
        for sa in accounts_to_delete:
            click.echo(f"{indent_1}Deleting '{sa['name']}' (ID: {sa['id']})...")
            
            if dry_run:
                click.echo(f"{indent_1*2}[DRY RUN] Would delete service account")
            else:
                try:
                    client.delete_project_service_account(project_id, sa['id'])
                    click.echo(f"{indent_1*2}[SUCCESS] Deleted successfully")
                except Exception as e:
                    click.echo(f"{indent_1*2}[ERROR] Failed to delete: {e}", err=True)
                    # Continue with other deletions
    else:
        click.echo(f"\n[STEP 3] No old service accounts to delete")
    
    # Step 4: Send notification if configured
    if notify_user_id and new_api_key_value:
        click.echo(f"\n[STEP 4] Sending notification to user {notify_user_id}...")
        
        if dry_run:
            click.echo(f"{indent_1}[DRY RUN] Would send Mattermost notification")
        else:
            try:
                from openai_admin.notifier import MattermostNotifier
                
                notifier = MattermostNotifier()
                
                # Format message
                message = f"""🔄 **OpenAI API Key Rotation Complete**

**Project ID:** `{project_id}`
**Service Account:** `{new_sa_name}`
**Service Account ID:** `{new_sa_id}`

**New API Key:**
```
{new_api_key_value}
```

⚠️ **Important:** Save this API key immediately in a secure location. It will not be shown again.

**Rotation Summary:**
- Created: {new_sa_name}
- Deleted: {len(accounts_to_delete)} old service account(s)

**Next Steps:**
1. Update your application configuration with the new API key
2. Test the new API key
3. Monitor for any issues
"""
                
                notifier.send_to_user(notify_user_id, message)
                click.echo(f"{indent_1}[SUCCESS] Notification sent via Mattermost")
                
            except Exception as e:
                click.echo(f"{indent_1}[ERROR] Failed to send notification: {e}", err=True)
                click.echo(f"{indent_1}[WARNING] Rotation completed but notification failed")
    elif notify_user_id and not new_api_key_value:
        click.echo(f"\n[STEP 4] Skipping notification (no API key to send)")
    else:
        click.echo(f"\n[STEP 4] No notification configured")
    
    # Summary
    click.echo(f"\n{'='*80}")
    click.echo(f"Rotation Summary")
    click.echo(f"{'='*80}")
    click.echo(f"Created:         {new_sa_name}")
    click.echo(f"Deleted:         {len(accounts_to_delete)} service account(s)")
    click.echo(f"Notification:    {'Sent' if notify_user_id and new_api_key_value and not dry_run else 'Skipped'}")
    click.echo(f"Status:          {'DRY RUN - No changes made' if dry_run else 'SUCCESS'}")
    click.echo(f"{'='*80}\n")


@rotation.command('list')
@click.argument('project_id')
@click.option('--prefix', help='Filter by naming prefix (e.g., api-key)')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
def list_rotated_keys(ctx, project_id, prefix, output_format):
    """List service accounts that match the rotation naming pattern
    
    Shows service accounts with names matching rotation patterns:
    - <prefix>-YY-MM (e.g., 'chatbot-server-24-11')
    - <prefix>-YYYY-MM-DD (e.g., 'api-key-2024-11-13')
    """
    client = ctx.obj['client']
    
    click.echo(f"Fetching service accounts for project {project_id}...")
    
    try:
        result = client.list_project_service_accounts(project_id, limit=100)
        all_service_accounts = result.get('data', [])
    except Exception as e:
        click.echo(f"[ERROR] Failed to fetch service accounts: {e}", err=True)
        sys.exit(1)
    
    # If prefix specified, filter
    if prefix:
        matching_accounts = _find_matching_service_accounts(all_service_accounts, prefix)
    else:
        # Try to find any date-based naming pattern
        matching_accounts = []
        for sa in all_service_accounts:
            name = sa.get('name', '')
            # Look for YY-MM or YYYY-MM-DD patterns at the end
            if re.search(r'-\d{2}-\d{2}$', name) or re.search(r'-\d{4}-\d{2}-\d{2}$', name):
                matching_accounts.append({
                    'id': sa.get('id'),
                    'name': name,
                    'created_at': sa.get('created_at'),
                    'role': sa.get('role')
                })
    
    if not matching_accounts:
        click.echo(f"\nNo service accounts found matching rotation pattern")
        return
    
    if output_format == 'json':
        click.echo(json.dumps(matching_accounts, indent=2, default=str))
    else:
        table_data = []
        for sa in matching_accounts:
            date_str = sa.get('date').strftime('%Y-%m-%d') if 'date' in sa else 'N/A'
            table_data.append([
                sa.get('id', 'N/A'),
                sa.get('name', 'N/A'),
                date_str,
                sa.get('role', 'N/A'),
                format_timestamp(sa.get('created_at'))
            ])
        
        headers = ['ID', 'Name', 'Date', 'Role', 'Created At']
        
        click.echo(f"\nTotal matching service accounts: {len(matching_accounts)}\n")
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))


@rotation.command('check')
@click.argument('project_id')
@click.argument('prefix')
@click.pass_context
def check_rotation_status(ctx, project_id, prefix):
    """Check rotation status for a project
    
    Shows current status of service accounts matching the rotation pattern.
    Helps identify if rotation is needed.
    """
    client = ctx.obj['client']
    
    indent_1 = ' ' * 3
    
    click.echo(f"Checking rotation status for project {project_id}...")
    
    try:
        result = client.list_project_service_accounts(project_id, limit=100)
        all_service_accounts = result.get('data', [])
    except Exception as e:
        click.echo(f"[ERROR] Failed to fetch service accounts: {e}", err=True)
        sys.exit(1)
    
    matching_accounts = _find_matching_service_accounts(all_service_accounts, prefix)
    
    click.echo(f"\n{'='*80}")
    click.echo(f"Rotation Status Report")
    click.echo(f"{'='*80}")
    click.echo(f"Project ID:       {project_id}")
    click.echo(f"Naming Prefix:    {prefix}")
    click.echo(f"Total Matching:   {len(matching_accounts)}")
    click.echo(f"{'='*80}\n")
    
    if not matching_accounts:
        click.echo("[INFO] No service accounts found with rotation naming pattern")
        click.echo(f"{indent_1}A new service account will be created on first rotation")
        return
    
    # Show current service accounts
    click.echo("Current Service Accounts:")
    for i, sa in enumerate(matching_accounts, 1):
        # Use actual creation timestamp for age calculation
        created_datetime = datetime.fromtimestamp(sa['created_at'])
        age_days = (datetime.now() - created_datetime).days
        status = "CURRENT" if i == 1 else "OLD"
        
        click.echo(f"\n{indent_1}{i}. {sa['name']}")
        click.echo(f"{indent_1*2}ID:         {sa['id']}")
        click.echo(f"{indent_1*2}Date:       {sa['date'].strftime('%Y-%m-%d')} (from name)")
        click.echo(f"{indent_1*2}Age:        {age_days} days")
        click.echo(f"{indent_1*2}Status:     {status}")
        click.echo(f"{indent_1*2}Created:    {format_timestamp(sa['created_at'])}")
    
    # Recommendations
    click.echo(f"\n{'='*80}")
    click.echo("Recommendations:")
    click.echo(f"{'='*80}")
    
    newest = matching_accounts[0]
    # Use actual creation timestamp for age calculation
    created_datetime = datetime.fromtimestamp(newest['created_at'])
    newest_age = (datetime.now() - created_datetime).days
    
    if newest_age == 0:
        click.echo(f"✓ Service account is current (created today)")
    elif newest_age <= 7:
        click.echo(f"✓ Service account is recent ({newest_age} days old)")
    elif newest_age <= 30:
        click.echo(f"⚠ Service account is {newest_age} days old - consider rotation")
    else:
        click.echo(f"⚠ Service account is {newest_age} days old - rotation recommended")
    
    if len(matching_accounts) > 2:
        old_count = len(matching_accounts) - 1
        click.echo(f"⚠ {old_count} old service account(s) will be deleted on next rotation")
    elif len(matching_accounts) == 2:
        click.echo(f"⚠ 1 old service account will be deleted on next rotation")
    
    click.echo(f"\n{'='*80}\n")


@rotation.command('batch')
@click.option('--config-file', type=click.Path(exists=True), required=True, help='Path to rotation configuration file')
@click.option('--action', type=click.Choice(['create', 'cleanup']), required=True, help='Action to perform: create new keys or cleanup old keys')
@click.option('--dry-run', is_flag=True, help='Show what would be done without making changes')
@click.option('--force', is_flag=True, help='Skip confirmation prompts')
@click.pass_context
def batch_rotation(ctx, config_file, action, dry_run, force):
    """Process multiple API key rotations from configuration file
    
    This command processes all rotations defined in your rotation.json file.
    Perfect for automated monthly key rotation across all projects.
    
    Configuration file structure:
      {
        "rotations": [
          {
            "project_name": "Inventory",
            "project_id": "proj_123",
            "keys": [
              {
                "name": "inventory-server",
                "notify_user": "49",
                "notify_channel": "mattermost",
                "date_format": "YY-MM"
              }
            ]
          }
        ]
      }
    
    Two-step workflow:
      Day 1:  python3 cli.py rotation batch --config rotation.json --action create
      Day 7:  python3 cli.py rotation batch --config rotation.json --action cleanup
    
    Examples:
        # Create all new keys (Day 1)
        python3 cli.py rotation batch --config config/rotation.json --action create
        
        # Preview cleanup
        python3 cli.py rotation batch --config config/rotation.json --action cleanup --dry-run
        
        # Cleanup all old keys (Day 7)
        python3 cli.py rotation batch --config config/rotation.json --action cleanup --force
    """
    client = ctx.obj['client']
    
    # Load configuration
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        click.echo(f"[ERROR] Failed to load config file: {e}", err=True)
        sys.exit(1)
    
    rotations = config.get('rotations', [])
    
    if not rotations:
        click.echo("[ERROR] No rotations found in config file", err=True)
        click.echo("[TIP] Expected structure: {'rotations': [...]}", err=True)
        sys.exit(1)
    
    # Count total operations
    total_projects = len(rotations)
    total_keys = sum(len(r.get('keys', [])) for r in rotations)
    
    # Show summary
    click.echo(f"\n{'='*80}")
    click.echo(f"Batch Rotation - {action.upper()}")
    click.echo(f"{'='*80}")
    click.echo(f"Config File:      {config_file}")
    click.echo(f"Projects:         {total_projects}")
    click.echo(f"Total Keys:       {total_keys}")
    click.echo(f"Action:           {action}")
    click.echo(f"Dry Run:          {dry_run}")
    click.echo(f"{'='*80}\n")
    
    if not force and not dry_run:
        click.echo(f"This will {action} {total_keys} API key(s) across {total_projects} project(s).")
        if not click.confirm('\nDo you want to continue?'):
            click.echo("Cancelled.")
            return
    
    # Track results
    results = {
        'success': [],
        'failed': [],
        'skipped': []
    }
    
    # Process each rotation
    for idx, rotation in enumerate(rotations, 1):
        project_name = rotation.get('project_name', 'Unknown')
        project_id = rotation.get('project_id')
        keys = rotation.get('keys', [])
        
        if not project_id:
            click.echo(f"\n[{idx}/{total_projects}] {project_name}: [ERROR] Missing project_id")
            results['failed'].append(f"{project_name}: Missing project_id")
            continue
        
        if not keys:
            click.echo(f"\n[{idx}/{total_projects}] {project_name}: [SKIP] No keys configured")
            results['skipped'].append(f"{project_name}: No keys")
            continue
        
        click.echo(f"\n{'='*80}")
        click.echo(f"[{idx}/{total_projects}] Processing: {project_name}")
        click.echo(f"{'='*80}")
        click.echo(f"Project ID:   {project_id}")
        click.echo(f"Keys:         {len(keys)}")
        click.echo("")
        
        # Process each key
        for key_idx, key_config in enumerate(keys, 1):
            key_name = key_config.get('name')
            notify_user = key_config.get('notify_user')
            notify_channel = key_config.get('notify_channel', 'mattermost')
            date_format = key_config.get('date_format', 'YY-MM')
            
            if not key_name:
                click.echo(f"  [{key_idx}/{len(keys)}] [ERROR] Missing key name")
                results['failed'].append(f"{project_name} / Key {key_idx}: Missing name")
                continue
            
            click.echo(f"  [{key_idx}/{len(keys)}] {key_name}")
            click.echo(f"    Format:       {date_format}")
            click.echo(f"    Notify:       {notify_user or 'None'} via {notify_channel}")
            
            try:
                if action == 'create':
                    # Call create command logic
                    _execute_create(
                        client, project_id, key_name, date_format,
                        notify_user if notify_channel == 'mattermost' else None,
                        dry_run, indent='    '
                    )
                    results['success'].append(f"{project_name} / {key_name}: Created")
                    
                elif action == 'cleanup':
                    # Call cleanup command logic
                    _execute_cleanup(
                        client, project_id, key_name, keep_latest=1,
                        dry_run=dry_run, indent='    '
                    )
                    results['success'].append(f"{project_name} / {key_name}: Cleaned up")
                
                click.echo(f"    [SUCCESS]")
                
            except Exception as e:
                click.echo(f"    [ERROR] {e}")
                results['failed'].append(f"{project_name} / {key_name}: {str(e)}")
        
        click.echo("")
    
    # Final summary
    click.echo(f"\n{'='*80}")
    click.echo(f"Batch Rotation Summary")
    click.echo(f"{'='*80}")
    click.echo(f"Successful:   {len(results['success'])}")
    click.echo(f"Failed:       {len(results['failed'])}")
    click.echo(f"Skipped:      {len(results['skipped'])}")
    click.echo(f"Status:       {'DRY RUN - No changes made' if dry_run else 'COMPLETE'}")
    click.echo(f"{'='*80}")
    
    if results['failed']:
        click.echo(f"\nFailed Operations:")
        for failure in results['failed']:
            click.echo(f"  ✗ {failure}")
    
    if results['skipped']:
        click.echo(f"\nSkipped:")
        for skipped in results['skipped']:
            click.echo(f"  - {skipped}")
    
    click.echo("")


def _execute_create(client, project_id, prefix, date_format, notify_user, dry_run, indent=''):
    """Helper function to execute key creation"""
    from openai_admin.notifier import MattermostNotifier
    
    # Fetch existing service accounts
    result = client.list_project_service_accounts(project_id, limit=100)
    all_service_accounts = result.get('data', [])
    matching_accounts = _find_matching_service_accounts(all_service_accounts, prefix)
    
    # Generate new service account name
    today = datetime.now()
    if date_format == 'YY-MM':
        new_sa_name = f"{prefix}-{today.strftime('%y-%m')}"
    else:
        new_sa_name = f"{prefix}-{today.strftime('%Y-%m-%d')}"
    
    # Check if already exists
    if any(sa['name'] == new_sa_name for sa in matching_accounts):
        click.echo(f"{indent}Already exists for current period, skipping creation")
        return
    
    click.echo(f"{indent}Creating: {new_sa_name}")
    
    if dry_run:
        click.echo(f"{indent}[DRY RUN] Would create service account")
        return
    
    # Create service account
    create_result = client.create_project_service_account(project_id, new_sa_name)
    new_sa_id = create_result.get('id')
    api_key = create_result.get('api_key', {})
    new_api_key_value = api_key.get('value')
    
    click.echo(f"{indent}Created: {new_sa_id}")
    
    # Send notification if configured
    if notify_user and new_api_key_value:
        try:
            notifier = MattermostNotifier()
            message = f"""🔑 **New OpenAI API Key Created**

**Project ID:** `{project_id}`
**Service Account:** `{new_sa_name}`
**Service Account ID:** `{new_sa_id}`

**New API Key:**
```
{new_api_key_value}
```

⚠️ **Important:** Save this API key immediately in a secure location.
"""
            notifier.send_to_user(notify_user, message)
            click.echo(f"{indent}Notification sent to user {notify_user}")
        except Exception as e:
            click.echo(f"{indent}[WARNING] Notification failed: {e}")


def _execute_cleanup(client, project_id, prefix, keep_latest, dry_run, indent=''):
    """Helper function to execute key cleanup"""
    # Fetch existing service accounts
    result = client.list_project_service_accounts(project_id, limit=100)
    all_service_accounts = result.get('data', [])
    matching_accounts = _find_matching_service_accounts(all_service_accounts, prefix)
    
    if not matching_accounts:
        click.echo(f"{indent}No keys found")
        return
    
    if len(matching_accounts) <= keep_latest:
        click.echo(f"{indent}Only {len(matching_accounts)} key(s), nothing to cleanup")
        return
    
    # Determine what to delete
    keys_to_delete = matching_accounts[keep_latest:]
    
    click.echo(f"{indent}Deleting {len(keys_to_delete)} old key(s)")
    
    for sa in keys_to_delete:
        if dry_run:
            click.echo(f"{indent}[DRY RUN] Would delete: {sa['name']}")
        else:
            client.delete_project_service_account(project_id, sa['id'])
            click.echo(f"{indent}Deleted: {sa['name']}")

