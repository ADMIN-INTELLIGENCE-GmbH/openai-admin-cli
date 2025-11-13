#!/usr/bin/env python3
"""
OpenAI Admin CLI - Main entry point
"""
import os
import sys
import logging
import click
from dotenv import load_dotenv

from openai_admin.client import OpenAIAdminClient

# Load environment variables from .env file
load_dotenv()

# Setup logging - log file in project root
project_root = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(project_root, 'openai_admin.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stderr) if os.getenv('DEBUG') else logging.NullHandler()
    ]
)
logger = logging.getLogger('openai_admin')


@click.group()
@click.option('--admin-key', envvar='OPENAI_ADMIN_KEY', help='OpenAI Admin API Key')
@click.option('--notify', help='User ID to notify (requires --channel)')
@click.option('--channel', type=click.Choice(['mattermost', 'email']), help='Notification channel (e.g., mattermost, email)')
@click.pass_context
def cli(ctx, admin_key, notify, channel):
    """OpenAI Admin CLI - Manage your OpenAI organization
    
    Author: Julian Billinger (ADMIN INTELLIGENCE)
    Support: julian.billinger@admin-intelligence.com
    """
    ctx.ensure_object(dict)
    try:
        ctx.obj['client'] = OpenAIAdminClient(admin_key)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    
    # Store notification settings in context
    ctx.obj['notify_user'] = notify
    ctx.obj['notify_channel'] = channel
    
    # Validate notification options
    if notify and not channel:
        click.echo("Error: --notify requires --channel", err=True)
        sys.exit(1)
    if channel and not notify:
        click.echo("Error: --channel requires --notify", err=True)
        sys.exit(1)


# Import and register command groups
from openai_admin.commands import users, projects, keys, service_accounts, rate_limits, usage, costs, audit, notify, rotation

cli.add_command(users.users)
cli.add_command(projects.projects)
cli.add_command(keys.keys)
cli.add_command(service_accounts.service_accounts)
cli.add_command(rate_limits.rate_limits)
cli.add_command(usage.usage)
cli.add_command(costs.costs_command)
cli.add_command(audit.audit)
cli.add_command(notify.notify)
cli.add_command(rotation.rotation)


if __name__ == '__main__':
    cli()
