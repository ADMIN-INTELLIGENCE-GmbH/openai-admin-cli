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

# Setup logging
log_file = 'openai_admin.log'
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
@click.pass_context
def cli(ctx, admin_key):
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


# Import and register command groups
from openai_admin.commands import users, projects, keys, service_accounts, rate_limits, usage, costs, audit

cli.add_command(users.users)
cli.add_command(projects.projects)
cli.add_command(keys.keys)
cli.add_command(service_accounts.service_accounts)
cli.add_command(rate_limits.rate_limits)
cli.add_command(usage.usage)
cli.add_command(costs.costs_command)
cli.add_command(audit.audit)


if __name__ == '__main__':
    cli()
