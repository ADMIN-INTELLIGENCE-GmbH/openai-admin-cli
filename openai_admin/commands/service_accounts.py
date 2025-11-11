"""Service Accounts commands"""
import click
import json
import sys
from datetime import datetime, timedelta
from tabulate import tabulate
from openai_admin.utils import format_timestamp, format_redacted_value, with_notification, notification_options
import requests

@click.group(name='service-accounts')
def service_accounts():
    """Manage service accounts"""
    pass


@service_accounts.command('list')
@click.argument('project_id')
@click.option('--limit', default=100, help='Maximum number of service accounts to return')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
@notification_options
@with_notification
def list_service_accounts(ctx, project_id, limit, output_format):
    """List all service accounts in a project"""
    client = ctx.obj['client']
    
    # Apply Progress Message Style
    click.echo(f"Fetching service accounts for project {project_id}...")
    result = client.list_project_service_accounts(project_id, limit=limit)
    
    accounts_data = result.get('data', [])
    
    if not accounts_data:
        # Apply Empty Results Style
        click.echo("No service accounts found for this project.")
        return
    
    if output_format == 'json':
        import json
        # Apply JSON Output Style
        click.echo(json.dumps(result, indent=2))
    else:
        # Table format
        table_data = []
        for sa in accounts_data:
            table_data.append([
                sa.get('id', 'N/A'),
                sa.get('name', 'N/A'),
                sa.get('role', 'N/A'),
                format_timestamp(sa.get('created_at'))
            ])
        
        # Apply Table Header Style (Title Case)
        headers = ['ID', 'Name', 'Role', 'Created At']
        
        # Apply Summary Lines Style
        click.echo(f"\nTotal service accounts: {len(accounts_data)}\n")
        
        # Apply Table Output Style (grid format)
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))


@service_accounts.command('create')
@click.argument('project_id')
@click.argument('name')
@click.pass_context
@notification_options
@with_notification
def create_service_account(ctx, project_id, name):
    """Create a new service account in a project
    
    This will create a service account and generate a new API key.
    The API key value is shown only once - save it immediately!
    """
    client = ctx.obj['client']
    
    # Apply Progress Message Style
    click.echo(f"Creating Service Account '{name}' in project {project_id}...") # Use full terminology
    
    # Define indentation levels
    indent_1 = ' ' * 3
    
    try:
        result = client.create_project_service_account(project_id, name)
        
        click.echo(f"\n{'='*80}")
        click.echo(f"[SUCCESS] Service Account Created Successfully!")
        click.echo(f"{'='*80}")
        
        # Consistent label-value alignment
        click.echo(f"ID:         {result.get('id')}")
        click.echo(f"Name:       {result.get('name')}")
        click.echo(f"Role:       {result.get('role')}")
        click.echo(f"Created At: {format_timestamp(result.get('created_at'))}")
        
        # Display API key if present
        api_key = result.get('api_key', {})
        if api_key and api_key.get('value'):
            click.echo(f"\n{'='*80}")
            click.echo(f"[WARNING] API KEY (SAVE THIS NOW - IT WON'T BE SHOWN AGAIN!)")
            click.echo(f"{'='*80}")
            
            # Consistent label-value alignment
            click.echo(f"Key ID:     {api_key.get('id')}")
            click.echo(f"Key Name:   {api_key.get('name')}")
            click.echo(f"[LOG] Key Value:  {api_key.get('value')}")
            click.echo(f"Created At: {format_timestamp(api_key.get('created_at'))}")
            click.echo(f"{'='*80}")
            
            click.echo(f"\n[WARNING] This API key value is displayed only once!")
            click.echo(f"{indent_1}Save it in a secure location immediately.")
            click.echo(f"{indent_1}If you lose it, you'll need to delete this Service Account")
            click.echo(f"{indent_1}and create a new one.\n")
        else:
            click.echo(f"\n[WARNING] No API key returned in response.")
    
    except Exception as e:
        click.echo(f"\n[ERROR] Error creating Service Account: {e}", err=True)
        sys.exit(1)


@service_accounts.command('get')
@click.argument('project_id')
@click.argument('service_account_id')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
@notification_options
@with_notification
def get_service_account(ctx, project_id, service_account_id, output_format):
    """Get details of a specific service account"""
    client = ctx.obj['client']
    
    click.echo(f"Fetching Service Account {service_account_id}...")
    try:
        sa = client.get_project_service_account(project_id, service_account_id)
    except Exception as e:
        click.echo(f"[ERROR] Failed to fetch Service Account {service_account_id}: {e}", err=True)
        sys.exit(1)
    
    if output_format == 'json':
        import json
        click.echo(json.dumps(sa, indent=2))
    else:
        click.echo(f"\n{'='*80}")
        click.echo(f"Service Account Details")
        click.echo(f"{'='*80}")
        
        # Consistent label-value alignment
        click.echo(f"ID:         {sa.get('id')}")
        click.echo(f"Name:       {sa.get('name')}")
        click.echo(f"Role:       {sa.get('role')}")
        click.echo(f"Created At: {format_timestamp(sa.get('created_at'))}")
        click.echo(f"{'='*80}\n")


@service_accounts.command('delete')
@click.argument('project_id')
@click.argument('service_account_id')
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
@notification_options
@with_notification
def delete_service_account(ctx, project_id, service_account_id, force):
    """Delete a service account from a project
    
    Warning: This will also delete all API keys associated with this service account.
    """
    client = ctx.obj['client']
    
    # Define indentation levels
    indent_1 = ' ' * 3
    
    # Get service account details first
    try:
        click.echo(f"Fetching Service Account {service_account_id} details...")
        sa = client.get_project_service_account(project_id, service_account_id)
        sa_name = sa.get('name', 'N/A')
    except Exception as e:
        click.echo(f"[ERROR] Error fetching Service Account {service_account_id}: {e}", err=True)
        sys.exit(1)
    
    # Show what will be deleted
    click.echo(f"\n[INFO] Service Account to delete:")
    
    click.echo(f"{indent_1}ID:   {service_account_id}")
    click.echo(f"{indent_1}Name: {sa_name}")
    click.echo(f"{indent_1}Role: {sa.get('role', 'N/A')}")
    
    # Confirm
    if not force:
        click.echo()
        click.echo("[WARNING] Deleting this Service Account will also delete all its API keys!")
        if not click.confirm('Are you sure you want to continue?'):
            click.echo("Cancelled.")
            return
    
    # Delete the service account
    click.echo(f"\n[INFO] Deleting Service Account '{sa_name}'...")
    try:
        client.delete_project_service_account(project_id, service_account_id)
        
        click.echo(f"\n[SUCCESS] Service Account '{sa_name}' deleted successfully.")
        click.echo(f"{indent_1}All associated API keys have been deleted.")
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            click.echo(f"\n[SUCCESS] Service Account '{sa_name}' deleted successfully.")
            click.echo(f"{indent_1}All associated API keys have been deleted.")
            click.echo(f"[NOTE] The API returned 404, but the Service Account is no longer present.")
        else:
            click.echo(f"\n[ERROR] Error deleting Service Account: {e}", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"\n[ERROR] Error deleting Service Account: {e}", err=True)
        sys.exit(1)