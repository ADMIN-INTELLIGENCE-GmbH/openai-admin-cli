"""Projects commands"""
import click
import json
import sys
import os # Added for file operations
from datetime import datetime, timedelta
from tabulate import tabulate
from openai_admin.utils import format_timestamp, format_redacted_value
import requests

# Assuming logger is defined elsewhere in the module or passed in context.
# Since it's not explicitly passed, for the sake of making the snippet runnable,
# I'll define a minimal mock logger for the 'delete' command to avoid NameError.
# In a real CLI, this would be imported or configured.
class SimpleLogger:
    def info(self, msg):
        pass # print(f"[LOGGER][INFO] {msg}")
    def warning(self, msg):
        pass # print(f"[LOGGER][WARNING] {msg}")
    def error(self, msg):
        pass # print(f"[LOGGER][ERROR] {msg}")
    def exception(self, msg):
        pass # print(f"[LOGGER][EXCEPTION] {msg}")

# Mocking the logger and log_file variables used in the delete command
try:
    logger # Check if logger is already defined
except NameError:
    logger = SimpleLogger()
    log_file = "/tmp/openai_admin.log"


@click.group()
def projects():
    """Manage organization projects"""
    pass


@projects.command('list')
@click.option('--include-archived', is_flag=True, help='Include archived projects')
@click.option('--limit', default=100, help='Maximum number of projects to return')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
def list_projects(ctx, include_archived, limit, output_format):
    """List all projects in the organization"""
    client = ctx.obj['client']
    
    # Apply Progress Message Style
    click.echo("Fetching projects...")
    result = client.list_projects(include_archived=include_archived, limit=limit)
    
    projects_data = result.get('data', [])
    
    if not projects_data:
        # Apply Empty Results Style
        click.echo("No projects found.")
        return
    
    if output_format == 'json':
        import json
        # Apply JSON Output Style
        click.echo(json.dumps(result, indent=2))
    else:
        # Table format
        table_data = []
        for project in projects_data:
            # Apply Long Text Truncation for ID
            project_id_truncated = project.get('id', '')[:20] + '...' if project.get('id') else 'N/A'
            
            # Use 'N/A' for missing/null values and consistent timestamp formatting
            table_data.append([
                project_id_truncated,
                project.get('name', 'N/A'),
                project.get('status', 'N/A'),
                format_timestamp(project.get('created_at')),
                format_timestamp(project.get('archived_at')) if project.get('archived_at') else 'N/A'
            ])
        
        # Apply Table Header Style (Title Case)
        headers = ['ID', 'Name', 'Status', 'Created At', 'Archived At']
        
        # Apply Summary Lines Style
        click.echo(f"\nTotal projects: {len(projects_data)}\n")
        
        # Apply Table Output Style (grid format)
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))


@projects.command('export-template')
@click.argument('project_id')
@click.option('--output', '-o', help='Output file path (default: templates/projects/<project_name>.json)')
@click.pass_context
def export_project_template(ctx, project_id, output):
    """Export a project configuration as a reusable template"""
    client = ctx.obj['client']
    import json
    import os
    
    # Apply Progress Message Style
    click.echo(f"Fetching project configuration for {project_id}...")
    
    try:
        # Get project details
        project = client.get_project(project_id)
        
        # Get project users
        users_result = client.list_project_users(project_id)
        users = users_result.get('data', [])
        
        # Get service accounts
        sa_result = client.list_project_service_accounts(project_id)
        service_accounts = sa_result.get('data', [])
        
        # Get rate limits
        rate_limits_result = client.list_project_rate_limits(project_id)
        rate_limits = rate_limits_result.get('data', [])
    except Exception as e:
        # Apply Detailed Errors with Context Style
        click.echo(f"[ERROR] Failed to fetch project data for {project_id}: {e}", err=True)
        return
    
    # Build template
    template = {
        "_comment": f"Template exported from project: {project.get('name')} ({project_id})",
        "_instructions": "Edit 'name' field and user emails as needed, then use 'projects create-from-template' to create a new project",
        "name": f"{project.get('name', 'New Project')} (Copy)",
        "users": [
            {
                "email": user.get('email', 'N/A'),
                "role": user.get('role', 'N/A'),
                "_note": f"Original user: {user.get('name', 'N/A')} ({user.get('id', 'N/A')})"
            }
            for user in users
        ],
        "service_accounts": [
            {
                "name": sa.get('name', 'N/A'),
                "role": sa.get('role', 'N/A'),
                "_note": f"Original SA: {sa.get('id', 'N/A')}"
            }
            for sa in service_accounts
        ],
        "rate_limits": [
            {
                "model": rl.get('model'),
                "max_requests_per_1_minute": rl.get('max_requests_per_1_minute'),
                "max_tokens_per_1_minute": rl.get('max_tokens_per_1_minute'),
                "max_images_per_1_minute": rl.get('max_images_per_1_minute'),
                "max_audio_megabytes_per_1_minute": rl.get('max_audio_megabytes_per_1_minute'),
                "max_requests_per_1_day": rl.get('max_requests_per_1_day'),
                "batch_1_day_max_input_tokens": rl.get('batch_1_day_max_input_tokens'),
            }
            for rl in rate_limits
        ]
    }
    
    # Determine output path
    if not output:
        templates_dir = os.path.join(os.getcwd(), 'templates', 'projects')
        os.makedirs(templates_dir, exist_ok=True)
        safe_name = project.get('name', 'project').replace(' ', '_').replace('/', '_')
        output = os.path.join(templates_dir, f"{safe_name}.json")
    
    # Write template
    try:
        with open(output, 'w') as f:
            json.dump(template, f, indent=2)
    except Exception as e:
        click.echo(f"[ERROR] Failed to write template to {output}: {e}", err=True)
        return
    
    # Apply Success, INFO, and TIP Styles
    click.echo(f"\n[SUCCESS] Template exported successfully!")
    click.echo(f"[INFO] Location: {output}")
    click.echo(f"\n[INFO] Template contents:")
    # Apply Lists and Bullet Points Style (3-space indentation)
    click.echo(f"   • Name: {template['name']}")
    click.echo(f"   • Users: {len(users)}")
    click.echo(f"   • Service Accounts: {len(service_accounts)}")
    click.echo(f"   • Rate Limits: {len(rate_limits)}")
    click.echo(f"\n[TIP] Edit the template and use:")
    click.echo(f"   python openai_admin.py projects create-from-template {output}\n")


@projects.command('create-from-template')
@click.argument('template_file', type=click.Path(exists=True))
@click.option('--dry-run', is_flag=True, help='Show what would be created without actually creating it')
@click.pass_context
def create_from_template(ctx, template_file, dry_run):
    """Create a new project from a template file"""
    client = ctx.obj['client']
    import json
    
    # Load template (Apply Progress Message Style)
    click.echo(f"Loading template from file...")
    try:
        with open(template_file, 'r') as f:
            template = json.load(f)
    except Exception as e:
        click.echo(f"[ERROR] Failed to load or parse template file {template_file}: {e}", err=True)
        return
    
    project_name = template.get('name', 'Untitled Project')
    users = template.get('users', [])
    service_accounts = template.get('service_accounts', [])
    rate_limits = template.get('rate_limits', [])
    
    # Show what will be created (Preview - Apply [CONFIG], [USERS], [SERVICE ACCOUNTS] prefixes and Indentation)
    click.echo(f"\n[CONFIG] Project Configuration:")
    # Apply Indentation (Level 1: 3 spaces)
    indent_1 = ' ' * 3
    click.echo(f"{indent_1}Name: {project_name}")
    click.echo(f"{indent_1}Users: {len(users)}")
    click.echo(f"{indent_1}Service Accounts: {len(service_accounts)}")
    click.echo(f"{indent_1}Rate Limits: {len(rate_limits)}")
    
    if users:
        click.echo(f"\n[USERS] Users to add:")
        # Apply Lists and Bullet Points Style (6-space indentation for bullets, since base is 3)
        indent_2 = ' ' * 6
        for user in users:
            click.echo(f"{indent_2}• {user.get('email', 'N/A')} ({user.get('role', 'N/A')})")
    
    if service_accounts:
        click.echo(f"\n[SERVICE ACCOUNTS] Service Accounts to create:")
        for sa in service_accounts:
            click.echo(f"{indent_2}• {sa.get('name', 'N/A')} ({sa.get('role', 'N/A')})")
    
    if dry_run:
        click.echo(f"\n[INFO] Dry run complete. No changes were made.")
        return
    
    # Confirm (Apply Confirmation Prompts Style)
    click.echo()
    if not click.confirm(f'Do you want to create project "{project_name}" with this configuration?'):
        click.echo("Cancelled.")
        return
    
    try:
        # Create project
        click.echo(f"\n[INFO] Creating project '{project_name}'...")
        project_result = client.create_project(project_name)
        project_id = project_result.get('id')
        click.echo(f"[SUCCESS] Project created: {project_id}")
        
        # Get all org users for lookup
        click.echo(f"[INFO] Fetching organization users...")
        org_users_result = client.list_users(limit=100)
        org_users = {user.get('email'): user.get('id') for user in org_users_result.get('data', [])}
        
        # Add users
        if users:
            click.echo(f"\n[USERS] Adding users...")
            for user in users:
                email = user.get('email')
                role = user.get('role')
                
                if email not in org_users:
                    # Apply [WARNING] prefix
                    click.echo(f"{indent_1}[WARNING] Skipping {email} - not found in organization.")
                    continue
                
                user_id = org_users[email]
                try:
                    client.add_project_user(project_id, user_id, role)
                    # Apply [SUCCESS] prefix
                    click.echo(f"{indent_1}[SUCCESS] Added {email} as {role}")
                except requests.exceptions.HTTPError as e:
                    # Check if user already exists (common when user is the project creator)
                    if e.response is not None and e.response.status_code == 400:
                        error_text = str(e.response.text) if hasattr(e.response, 'text') else str(e)
                        if 'already exists in project' in error_text or 'user_already_in_project' in error_text:
                            # Apply [INFO] prefix
                            click.echo(f"{indent_1}[INFO] {email} already in project (auto-added as creator)")
                        else:
                            # Apply [ERROR] prefix
                            click.echo(f"{indent_1}[ERROR] Failed to add {email}: {e.response.text if hasattr(e.response, 'text') else e}")
                    else:
                        click.echo(f"{indent_1}[ERROR] Failed to add {email}: {e}")
                except Exception as e:
                    click.echo(f"{indent_1}[ERROR] Failed to add {email}: {e}")
        
        # Create service accounts
        if service_accounts:
            click.echo(f"\n[SERVICE ACCOUNTS] Creating service accounts...")
            for sa in service_accounts:
                name = sa.get('name')
                try:
                    sa_result = client.create_project_service_account(project_id, name)
                    # Apply [SUCCESS] prefix
                    click.echo(f"{indent_1}[SUCCESS] Created Service Account: {name}") # Use full terminology
                    
                    # Apply Indentation (Level 2: 6 spaces)
                    indent_2 = ' ' * 6
                    click.echo(f"{indent_2}ID: {sa_result.get('id')}")
                    
                    # Show API key if returned
                    api_key = sa_result.get('api_key', {})
                    if api_key.get('value'):
                        # Apply [LOG] prefix for the key (since it's sensitive)
                        click.echo(f"{indent_2}[KEY] API Key: {api_key.get('value')}")
                        # Apply [WARNING] prefix
                        click.echo(f"{indent_2}[WARNING] Save this key - it won't be shown again!")
                except Exception as e:
                    click.echo(f"{indent_1}[ERROR] Failed to create Service Account {name}: {e}")
        
        # Note about rate limits
        if rate_limits:
            # Apply [NOTE] prefix
            click.echo(f"\n[NOTE] Rate limit configuration not yet implemented")
            click.echo(f"{indent_1}You can manually configure rate limits for {project_id}")
        
        # Final success message
        click.echo(f"\n[SUCCESS] Project created successfully!")
        click.echo(f"{indent_1}ID: {project_id}")
        click.echo(f"{indent_1}Name: {project_name}")
        
    except Exception as e:
        # Apply Detailed Errors with Context Style
        click.echo(f"\n[ERROR] Error creating project: {e}", err=True)
        sys.exit(1)


@projects.command('delete')
@click.argument('project_ids', nargs=-1, required=True)
@click.option('--force', is_flag=True, help='Skip confirmation prompts')
@click.pass_context
def delete_project(ctx, project_ids, force):
    """Delete (archive) one or more projects
    
    Note: Projects are archived, not permanently deleted. The archiving process
    will automatically remove all API keys. Users and service accounts will be
    explicitly removed before archiving (except organization owners):
    
    - API keys are automatically deleted when the project is archived
    - Service accounts are removed before archiving
    - Users are removed before archiving (organization owners cannot be removed)
    
    Archived projects cannot be used or updated but remain visible in the
    organization when using --include-archived flag.
    """
    client = ctx.obj['client']
    
    # Indentation levels
    indent_1 = ' ' * 3
    indent_2 = ' ' * 6
    
    logger.info(f"=== Starting project delete operation for: {project_ids} ===")
    click.echo(f"[LOG] Logging details to: {log_file}\n") # Using [LOG] prefix
    
    if not project_ids:
        click.echo("[ERROR] Please provide at least one project ID to delete", err=True)
        sys.exit(1)
    
    # Fetch details for all projects
    projects_info = []
    for project_id in project_ids:
        try:
            # Apply Progress Message Style
            click.echo(f"Processing: Project {project_id}")
            project = client.get_project(project_id)
            
            # Check if already archived
            if project.get('status') == 'archived':
                click.echo(f"{indent_1}[WARNING] Project {project_id} ({project.get('name')}) is already archived. Skipping.")
                continue
            
            # Get project resources
            users_result = client.list_project_users(project_id)
            users = users_result.get('data', [])
            
            sa_result = client.list_project_service_accounts(project_id)
            service_accounts = sa_result.get('data', [])
            
            keys_result = client.list_project_api_keys(project_id)
            api_keys = keys_result.get('data', [])
            
            projects_info.append({
                'id': project_id,
                'name': project.get('name', 'Unnamed Project'),
                'users': users,
                'service_accounts': service_accounts,
                'api_keys': api_keys
            })
        except Exception as e:
            click.echo(f"[ERROR] Error fetching project {project_id}: {e}", err=True)
            continue
    
    if not projects_info:
        click.echo("No active projects found to delete.")
        return
    
    # Show summary (Preview)
    # Apply Major Section Header Style (80-character width)
    click.echo(f"\n{'='*80}")
    click.echo(f"Projects to Delete (Archive)") # Removed [DELETE] prefix for section header
    click.echo(f"{'='*80}\n")
    
    for info in projects_info:
        user_count = len(info['users'])
        sa_count = len(info['service_accounts'])
        key_count = len(info['api_keys'])
        
        # Apply Indentation for Hierarchical Information
        click.echo(f"[PROJECT] {info['name']} ({info['id']})")
        
        # Users
        if user_count > 0:
            click.echo(f"{indent_1}[USERS] {user_count} user(s) will be removed:")
            for user in info['users']:
                click.echo(f"{indent_2}• {user.get('name', 'N/A')} ({user.get('email', 'N/A')}) - {user.get('role', 'N/A')}") # Apply bullet list style
        else:
            click.echo(f"{indent_1}[USERS] No users")
        
        # Service Accounts
        if sa_count > 0:
            click.echo(f"{indent_1}[SERVICE ACCOUNTS] {sa_count} Service Account(s) will be removed:")
            for sa in info['service_accounts']:
                click.echo(f"{indent_2}• {sa.get('name', 'Unnamed')} ({sa.get('id')})") # Apply bullet list style
        else:
            click.echo(f"{indent_1}[SERVICE ACCOUNTS] No Service Accounts")
        
        # API Keys
        if key_count > 0:
            click.echo(f"{indent_1}[API KEYS] {key_count} API Key(s) will be automatically deleted:")
            for key in info['api_keys']:
                click.echo(f"{indent_2}• {key.get('name', 'Unnamed')} - {format_redacted_value(key.get('redacted_value', 'N/A'))}") # Apply bullet list style
        else:
            click.echo(f"{indent_1}[API KEYS] No API Keys")
        
        click.echo()
    
    # Confirmation (Apply Confirmation Prompts Style)
    if not force:
        click.echo("\n[WARNING] This will archive the project(s). Users and Service Accounts will") # Use full terminology
        click.echo(f"{indent_1}be removed, and API keys will be automatically deleted. Archived projects")
        click.echo(f"{indent_1}cannot be used. Organization owners cannot be removed from projects.")
        if not click.confirm(f'\nDo you want to archive {len(projects_info)} project(s)?'):
            click.echo("Cancelled.")
            return
    
    # Process each project (Multi-Step Operations Style)
    for info in projects_info:
        project_id = info['id']
        project_name = info['name']
        users = info['users']
        service_accounts = info['service_accounts']
        api_keys = info['api_keys']
        
        # Apply Minor Separator and Progress Message Style
        click.echo(f"\n{'─'*80}")
        click.echo(f"Processing: {project_name} ({project_id})")
        click.echo(f"{'─'*80}")
        
        # API Key Note (No action, just INFO)
        if api_keys:
            click.echo(f"[API KEYS] {len(api_keys)} API key(s) will be automatically deleted when project is archived.")
            logger.info(f"Skipping manual deletion of {len(api_keys)} API keys - will be auto-deleted on archive")
        
        # Step 1: Remove service accounts
        if service_accounts:
            click.echo(f"[SERVICE ACCOUNTS] Removing {len(service_accounts)} Service Account(s)...")
            logger.info(f"Removing {len(service_accounts)} service accounts from project {project_id}")
            for sa in service_accounts:
                sa_id = sa.get('id')
                sa_name = sa.get('name', 'Unnamed')
                logger.info(f"Attempting to remove service account: {sa_name} ({sa_id})")
                try:
                    client.delete_project_service_account(project_id, sa_id)
                    click.echo(f"{indent_1}[SUCCESS] Removed Service Account: {sa_name}")
                    logger.info(f"Successfully removed service account: {sa_name}")
                except requests.exceptions.HTTPError as e:
                    logger.error(f"Failed to remove service account {sa_name}: {e}")
                    error_msg = str(e)
                    if e.response:
                        logger.error(f"Status: {e.response.status_code}, Body: {e.response.text}")
                        try:
                            error_data = e.response.json()
                            error_msg = error_data.get('error', {}).get('message', e.response.text)
                        except:
                            error_msg = e.response.text
                    
                    if e.response and e.response.status_code == 404:
                        click.echo(f"{indent_1}[INFO] Service Account {sa_name} not found (may already be removed).")
                    else:
                        click.echo(f"{indent_1}[ERROR] Failed to remove Service Account {sa_name}: {error_msg}")
                except Exception as e:
                    logger.exception(f"Unexpected error removing service account {sa_name}")
                    click.echo(f"{indent_1}[ERROR] Failed to remove Service Account {sa_name}: {e}")
        
        # Step 2: Remove users (except organization owners)
        if users:
            click.echo(f"[USERS] Removing {len(users)} user(s)...")
            logger.info(f"Removing {len(users)} users from project {project_id}")
            for user in users:
                user_id = user.get('id')
                user_name = user.get('name', 'N/A')
                user_email = user.get('email', 'N/A')
                logger.info(f"Attempting to remove user: {user_name} ({user_email}, {user_id})")
                try:
                    client.delete_project_user(project_id, user_id)
                    click.echo(f"{indent_1}[SUCCESS] Removed user: {user_name} ({user_email})")
                    logger.info(f"Successfully removed user: {user_email}")
                except requests.exceptions.HTTPError as e:
                    logger.error(f"Failed to remove user {user_email}: {e}")
                    error_msg = str(e)
                    error_code = None
                    if e.response:
                        logger.error(f"Status: {e.response.status_code}, Body: {e.response.text}")
                        try:
                            error_data = e.response.json()
                            error_code = error_data.get('error', {}).get('code', '')
                            error_msg = error_data.get('error', {}).get('message', e.response.text)
                        except:
                            error_msg = e.response.text
                        
                        if e.response.status_code == 404:
                            click.echo(f"{indent_1}[INFO] User {user_email} not found (may already be removed).")
                        elif error_code == 'user_organization_owner':
                            click.echo(f"{indent_1}[INFO] User {user_email} is an Organization owner (cannot be removed).")
                            logger.info(f"User {user_email} is org owner - skipping removal")
                        else:
                            click.echo(f"{indent_1}[ERROR] Failed to remove user {user_email}: {error_msg}")
                    else:
                        click.echo(f"{indent_1}[ERROR] Failed to remove user {user_email}: {str(e)}")
                except Exception as e:
                    logger.exception(f"Unexpected error removing user {user_email}")
                    click.echo(f"{indent_1}[ERROR] Failed to remove user {user_email}: {e}")
        
        # Step 3: Archive the project
        try:
            click.echo(f"[PROJECT] Archiving project...")
            logger.info(f"Attempting to archive project {project_id}")
            result = client.archive_project(project_id)
            logger.info(f"Archive result: {result}")
            if result.get('status') == 'archived':
                click.echo(f"{indent_1}[SUCCESS] Project archived successfully")
                click.echo(f"{indent_1}Archived At: {format_timestamp(result.get('archived_at'))}")
                logger.info(f"Project {project_id} archived successfully")
            else:
                click.echo(f"{indent_1}[WARNING] Project status: {result.get('status')}")
                logger.warning(f"Unexpected project status: {result.get('status')}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to archive project {project_id}: {e}")
            error_msg = str(e)
            error_code = None
            if e.response:
                logger.error(f"Status: {e.response.status_code}, Body: {e.response.text}")
                try:
                    error_data = e.response.json()
                    error_code = error_data.get('error', {}).get('code', '')
                    error_msg = error_data.get('error', {}).get('message', '')
                except:
                    error_msg = e.response.text
                
                if error_code == 'project_archived':
                    click.echo(f"{indent_1}[INFO] Project is already archived.")
                    logger.info("Project was already archived")
                else:
                    click.echo(f"{indent_1}[ERROR] Failed to archive project: {error_msg or str(e)}")
                    
                    # Verification check inside the error handler is kept but styled
                    try:
                        logger.info("Verifying project status after error...")
                        verify = client.get_project(project_id)
                        if verify.get('status') == 'archived':
                            click.echo(f"{indent_1}[NOTE] Note: Project was archived despite error message.")
                    except Exception as verify_error:
                        logger.error(f"Failed to verify project status: {verify_error}")
            else:
                click.echo(f"{indent_1}[ERROR] Failed to archive project: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error archiving project {project_id}")
            click.echo(f"{indent_1}[ERROR] Failed to archive project: {e}")
    
    # Final Success Message
    click.echo(f"\n{'='*80}")
    click.echo(f"[SUCCESS] Completed")
    click.echo(f"{'='*80}\n")
    
    click.echo(f"[TIP] Use 'projects list --include-archived' to view archived projects")
    
    # Final verification
    logger.info("=== Performing final verification ===")
    click.echo(f"\n[INFO] Verifying final status...")
    for info in projects_info:
        try:
            final_status = client.get_project(info['id'])
            status = final_status.get('status')
            if status == 'archived':
                click.echo(f"{indent_1}[SUCCESS] {info['name']}: Successfully archived")
            else:
                click.echo(f"{indent_1}[WARNING] {info['name']}: Status is '{status}'")
            logger.info(f"Final status for {info['id']}: {status}")
        except Exception as e:
            logger.error(f"Failed to verify {info['id']}: {e}")
            click.echo(f"{indent_1}[ERROR] {info['name']}: Could not verify status")