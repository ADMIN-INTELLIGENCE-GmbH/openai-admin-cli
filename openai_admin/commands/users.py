"""Users commands"""
import click
import json
import sys
from datetime import datetime, timedelta
from tabulate import tabulate
from openai_admin.utils import format_timestamp, format_redacted_value
import requests

@click.group()
def users():
    """Manage organization users"""
    pass


@users.command('list')
@click.option('--limit', default=100, help='Maximum number of users to return')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
def list_users(ctx, limit, output_format):
    """List all users in the organization"""
    client = ctx.obj['client']
    
    # Apply Progress Message Style
    click.echo("Fetching users...")
    result = client.list_users(limit=limit)
    
    users_data = result.get('data', [])
    
    if not users_data:
        # Apply Empty Results Style
        click.echo("No users found.")
        return
    
    if output_format == 'json':
        import json
        # Apply JSON Output Style
        click.echo(json.dumps(result, indent=2))
    else:
        # Table format
        table_data = []
        for user in users_data:
            # Apply Long Text Truncation for ID
            user_id_truncated = user.get('id', '')[:20] + '...' if user.get('id') else 'N/A'
            
            table_data.append([
                user_id_truncated,
                user.get('name', 'N/A'),
                user.get('email', 'N/A'),
                user.get('role', 'N/A'),
                format_timestamp(user.get('added_at'))
            ])
        
        # Apply Table Header Style (Title Case)
        headers = ['ID', 'Name', 'Email', 'Role', 'Added At']
        
        # Apply Summary Lines Style
        click.echo(f"\nTotal users: {len(users_data)}\n")
        
        # Apply Table Output Style (grid format)
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))