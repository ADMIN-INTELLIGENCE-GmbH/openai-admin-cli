"""Keys commands"""
import click
import json
import sys
from datetime import datetime, timedelta
from tabulate import tabulate
from openai_admin.utils import format_timestamp, format_redacted_value, with_notification, notification_options
import requests

@click.group()
def keys():
    """Manage API keys"""
    pass


@keys.command('list-admin')
@click.option('--limit', default=100, help='Maximum number of keys to return')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
@notification_options
@with_notification
def list_admin_keys(ctx, limit, output_format):
    """List all admin API keys"""
    client = ctx.obj['client']
    
    # Apply Progress Message Style
    click.echo("Fetching admin API keys...")
    result = client.list_admin_keys(limit=limit)
    
    keys_data = result.get('data', [])
    
    if not keys_data:
        # Apply Empty Results Style
        click.echo("No admin API keys found.")
        return
    
    if output_format == 'json':
        import json
        # Apply JSON Output Style
        click.echo(json.dumps(result, indent=2))
    else:
        # Table format
        table_data = []
        for key in keys_data:
            owner = key.get('owner', {})
            owner_type = owner.get('type', 'N/A')
            owner_name = 'N/A'
            
            if owner_type == 'user':
                owner_name = owner.get('name', 'N/A')
            elif owner_type == 'service_account':
                owner_name = owner.get('name', 'N/A')
            
            table_data.append([
                key.get('id', 'N/A'),
                key.get('name', 'N/A'),
                format_redacted_value(key.get('redacted_value', '')),
                owner_type,
                owner_name,
                format_timestamp(key.get('created_at')),
                format_timestamp(key.get('last_used_at'))
            ])
        
        # Apply Table Header Style (Title Case)
        headers = ['ID', 'Name', 'Redacted Value', 'Owner Type', 'Owner', 'Created At', 'Last Used']
        
        # Apply Summary Lines Style
        click.echo(f"\nTotal admin keys: {len(keys_data)}\n")
        
        # Apply Table Output Style (grid format)
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))


@keys.command('list-project')
@click.argument('project_id')
@click.option('--limit', default=100, help='Maximum number of keys to return')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
@notification_options
@with_notification
def list_project_keys(ctx, project_id, limit, output_format):
    """List API keys for a specific project"""
    client = ctx.obj['client']
    
    # Apply Progress Message Style
    click.echo(f"Fetching API keys for project {project_id}...")
    result = client.list_project_api_keys(project_id, limit=limit)
    
    keys_data = result.get('data', [])
    
    if not keys_data:
        # Apply Empty Results Style
        click.echo(f"No API keys found for project {project_id}.") # Added project_id context
        return
    
    if output_format == 'json':
        import json
        # Apply JSON Output Style
        click.echo(json.dumps(result, indent=2))
    else:
        # Table format
        table_data = []
        for key in keys_data:
            owner = key.get('owner', {})
            owner_type = owner.get('type', 'N/A')
            owner_name = 'N/A'
            
            if owner_type == 'user':
                user_data = owner.get('user', {})
                owner_name = user_data.get('name', 'N/A')
            elif owner_type == 'service_account':
                sa_data = owner.get('service_account', {})
                owner_name = sa_data.get('name', 'N/A')
            
            table_data.append([
                key.get('id', 'N/A'),
                key.get('name', 'N/A'),
                format_redacted_value(key.get('redacted_value', '')),
                owner_type,
                owner_name,
                format_timestamp(key.get('created_at')),
                format_timestamp(key.get('last_used_at'))
            ])
        
        # Apply Table Header Style (Title Case)
        headers = ['ID', 'Name', 'Redacted Value', 'Owner Type', 'Owner', 'Created At', 'Last Used']
        
        # Apply Summary Lines Style
        click.echo(f"\nTotal project keys: {len(keys_data)}\n")
        
        # Apply Table Output Style (grid format)
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))


@keys.command('get')
@click.argument('project_id')
@click.argument('key_id')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
@notification_options
@with_notification
def get_project_key(ctx, project_id, key_id, output_format):
    """Get details of a specific API key"""
    client = ctx.obj['client']
    
    click.echo(f"Fetching API key {key_id} from project {project_id}...")
    try:
        key = client.get_project_api_key(project_id, key_id)
    except Exception as e:
        click.echo(f"[ERROR] Failed to fetch key {key_id}: {e}", err=True)
        sys.exit(1)
    
    if output_format == 'json':
        import json
        # Apply JSON Output Style
        click.echo(json.dumps(key, indent=2))
    else:
        # Detailed view
        owner = key.get('owner', {})
        owner_type = owner.get('type', 'N/A')
        
        # Apply Major Section Header Style (80-character width)
        click.echo(f"\n{'='*80}")
        click.echo(f"API Key Details")
        click.echo(f"{'='*80}")
        
        # Consistent label-value alignment
        click.echo(f"ID:              {key.get('id')}")
        click.echo(f"Name:            {key.get('name')}")
        click.echo(f"Redacted Value:  {format_redacted_value(key.get('redacted_value', ''))}")
        click.echo(f"Created At:      {format_timestamp(key.get('created_at'))}")
        click.echo(f"Last Used At:    {format_timestamp(key.get('last_used_at'))}")
        click.echo(f"\nOwner Type:      {owner_type}")
        
        if owner_type == 'user':
            user = owner.get('user', {})
            click.echo(f"Owner Name:      {user.get('name', 'N/A')}")
            click.echo(f"Owner Email:     {user.get('email', 'N/A')}")
            click.echo(f"Owner Role:      {user.get('role', 'N/A')}")
        elif owner_type == 'service_account':
            sa = owner.get('service_account', {})
            click.echo(f"Service Account: {sa.get('name', 'N/A')}") # Use full terminology
            click.echo(f"Account ID:      {sa.get('id', 'N/A')}")
            click.echo(f"Account Role:    {sa.get('role', 'N/A')}")
        
        click.echo(f"{'='*80}\n")


@keys.command('delete')
@click.argument('project_id')
@click.argument('key_id')
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
@notification_options
@with_notification
def delete_project_key(ctx, project_id, key_id, force):
    """Delete an API key from a project
    
    Note: Cannot delete service account API keys. To remove a service account's
    key, delete the entire service account using 'service-accounts delete'.
    """
    client = ctx.obj['client']
    
    # Get key details first
    try:
        key = client.get_project_api_key(project_id, key_id)
    except Exception as e:
        click.echo(f"[ERROR] Error fetching key {key_id}: {e}", err=True)
        sys.exit(1)
    
    owner = key.get('owner', {})
    owner_type = owner.get('type', 'N/A')
    key_name = key.get('name', 'N/A')
    
    # Check if it's a service account key
    if owner_type == 'service_account':
        sa = owner.get('service_account', {})
        sa_id = sa.get('id', 'N/A')
        
        click.echo(f"[ERROR] Failed to delete API key {key_id}: Key belongs to Service Account '{sa.get('name', 'N/A')}' ({sa_id}).", err=True)
        click.echo(f"[NOTE] Service Account keys cannot be deleted individually.", err=True)
        click.echo(f"[TIP] To remove this key, delete the entire Service Account:", err=True)
        click.echo(f"   python openai_admin.py service-accounts delete {project_id} {sa_id}", err=True)
        sys.exit(1)
    
    # Show what will be deleted
    click.echo(f"\n[INFO] API Key to delete:")
    
    indent_1 = ' ' * 3
    click.echo(f"{indent_1}ID:   {key_id}")
    click.echo(f"{indent_1}Name: {key_name}")
    
    if owner_type == 'user':
        user = owner.get('user', {})
        click.echo(f"{indent_1}User: {user.get('email', 'N/A')}")
    
    if not force:
        if not click.confirm(f'\nDo you want to delete API key {key_id}?'):
            click.echo("Cancelled.")
            return
    
    # Delete the key
    click.echo(f"\nDeleting API key {key_id}...")
    try:
        client.delete_project_api_key(project_id, key_id)
        click.echo(f"\n[SUCCESS] API key deleted successfully.")
    except Exception as e:
        click.echo(f"\n[ERROR] Error deleting key: {e}", err=True)
        sys.exit(1)