import click
import json
import sys
from datetime import datetime, timedelta
from tabulate import tabulate
from openai_admin.utils import format_timestamp, format_redacted_value
import requests

@click.group()
def audit():
    """View audit logs"""
    pass


@audit.command('list')
@click.option('--limit', default=20, help='Maximum number of logs to return (1-100)')
@click.option('--after', help='Cursor for pagination (object ID)')
@click.option('--before', help='Cursor for pagination (object ID)')
@click.option('--start-date', help='Filter events from this date (YYYY-MM-DD)')
@click.option('--end-date', help='Filter events until this date (YYYY-MM-DD)')
@click.option('--days', type=int, help='Alternative: look back N days from now')
@click.option('--event-type', multiple=True, help='Filter by event type (e.g., project.created, user.added)')
@click.option('--project-id', multiple=True, help='Filter by project ID')
@click.option('--actor-email', multiple=True, help='Filter by actor email address')
@click.option('--actor-id', multiple=True, help='Filter by actor ID (user, service account, or API key)')
@click.option('--resource-id', multiple=True, help='Filter by resource ID')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'detailed']), default='table', help='Output format')
@click.pass_context
def list_audit_logs(ctx, limit, after, before, start_date, end_date, days, event_type, 
                   project_id, actor_email, actor_id, resource_id, output_format):
    """List audit logs for security and compliance monitoring"""
    client = ctx.obj['client']
    
    from datetime import datetime, timedelta
    
    # Handle date filters
    effective_at_gte = None
    effective_at_lt = None
    
    if days:
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days)
        effective_at_gte = int(start_dt.timestamp())
        effective_at_lt = int(end_dt.timestamp())
    elif start_date or end_date:
        try:
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                effective_at_gte = int(start_dt.timestamp())
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                effective_at_lt = int(end_dt.timestamp())
        except ValueError as e:
            # Apply Error Message Style
            click.echo(f"[ERROR] Error parsing date: {e}", err=True)
            click.echo("Use format: YYYY-MM-DD", err=True)
            return
    
    # Apply Progress Message Style
    click.echo("Fetching audit logs...")
    result = client.list_audit_logs(
        limit=limit,
        after=after,
        before=before,
        effective_at_gte=effective_at_gte,
        effective_at_lt=effective_at_lt,
        event_types=list(event_type) if event_type else None,
        project_ids=list(project_id) if project_id else None,
        actor_emails=list(actor_email) if actor_email else None,
        actor_ids=list(actor_id) if actor_id else None,
        resource_ids=list(resource_id) if resource_id else None
    )
    
    logs_data = result.get('data', [])
    
    if not logs_data:
        # Apply Empty Results Style
        click.echo("No audit logs found.")
        return
    
    if output_format == 'json':
        import json
        # Apply JSON Output Style
        click.echo(json.dumps(result, indent=2))
        return
    
    if output_format == 'detailed':
        # Apply Detailed Output Format (Major Section Header)
        click.echo(f"\n{'='*100}")
        click.echo(f"Audit Logs - {len(logs_data)} events")
        click.echo(f"{'='*100}\n")
        
        for log in logs_data:
            # Apply Minor Separator
            click.echo(f"{'─'*100}")
            click.echo(f"ID: {log.get('id')}")
            click.echo(f"Type: {log.get('type')}")
            click.echo(f"Time: {format_timestamp(log.get('effective_at'))}")
            
            # Actor information
            actor = log.get('actor', {})
            actor_type = actor.get('type', 'unknown')
            click.echo(f"Actor Type: {actor_type}")
            
            # Apply Indentation (Level 1: 3 spaces)
            indent_1 = ' ' * 3
            if actor_type == 'session':
                session = actor.get('session', {})
                user = session.get('user', {})
                click.echo(f"{indent_1}User: {user.get('email', 'N/A')} (ID: {user.get('id', 'N/A')})")
                click.echo(f"{indent_1}IP: {session.get('ip_address', 'N/A')}")
                if session.get('user_agent'):
                    # Apply Long Text Truncation
                    click.echo(f"{indent_1}User Agent: {session.get('user_agent')[:80]}...")
            elif actor_type == 'api_key':
                api_key = actor.get('api_key', {})
                key_type = api_key.get('type', 'unknown')
                if key_type == 'user':
                    user = api_key.get('user', {})
                    click.echo(f"{indent_1}User: {user.get('email', 'N/A')} (ID: {user.get('id', 'N/A')})")
                elif key_type == 'service_account':
                    sa = api_key.get('service_account', {})
                    click.echo(f"{indent_1}Service Account: {sa.get('id', 'N/A')}")
            
            # Project context
            project = log.get('project')
            if project:
                click.echo(f"Project: {project.get('id', 'N/A')} - {project.get('name', 'N/A')}")
            
            # Event-specific data
            event_type_key = log.get('type')
            if event_type_key in log:
                event_data = log.get(event_type_key, {})
                if event_data:
                    click.echo(f"Details: {event_data}")
            
            click.echo()
        
        click.echo(f"{'─'*100}")
        
        if result.get('has_more'):
            click.echo(f"\n[WARNING] More logs available. Use --after={result.get('last_id')} to fetch next page")
            click.echo(f"Or use --format=detailed for more information about each event\n")
        
        return
    
    # Table format (compact)
    table_data = []
    for log in logs_data:
        actor = log.get('actor', {})
        actor_type = actor.get('type', 'unknown')
        
        # Extract actor identifier
        actor_info = 'N/A'
        if actor_type == 'session':
            session = actor.get('session', {})
            user = session.get('user', {})
            actor_info = user.get('email', 'N/A')
        elif actor_type == 'api_key':
            api_key = actor.get('api_key', {})
            if api_key.get('type') == 'user':
                user = api_key.get('user', {})
                actor_info = user.get('email', 'N/A')
            elif api_key.get('type') == 'service_account':
                sa = api_key.get('service_account', {})
                # Use full terminology "Service Account" in messages, SA abbreviation here is contextual
                actor_info = f"SA: {sa.get('id', 'N/A')}" 
        
        # Get project if available
        project = log.get('project', {})
        project_name = project.get('name', '') if project else ''
        
        table_data.append([
            log.get('id', '')[:20] + '...',  # Truncate ID
            format_timestamp(log.get('effective_at')),
            log.get('type', ''),
            actor_type,
            actor_info[:30],  # Truncate actor info
            project_name[:20] if project_name else 'N/A'
        ])
    
    # Apply Table Header Style (Title Case is already used)
    headers = ['ID', 'Time', 'Event Type', 'Actor Type', 'Actor', 'Project']
    
    # Apply Summary Lines Style
    click.echo(f"\nTotal logs: {len(logs_data)}\n")
    
    # Apply Table Output Style (grid format)
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    if result.get('has_more'):
        click.echo(f"\n[WARNING] More logs available. Use --after={result.get('last_id')} to fetch next page")
        click.echo(f"Or use --format=detailed for more information about each event\n")


@audit.command('event-types')
def list_event_types():
    """List common audit log event types"""
    event_types = {
        "API Keys": [
            "api_key.created",
            "api_key.updated",
            "api_key.deleted",
        ],
        "Users": [
            "user.added",
            "user.updated",
            "user.deleted",
        ],
        "Projects": [
            "project.created",
            "project.updated",
            "project.archived",
            "project.deleted",
        ],
        "Invites": [
            "invite.sent",
            "invite.accepted",
            "invite.deleted",
        ],
        "Service Accounts": [
            "service_account.created",
            "service_account.updated",
            "service_account.deleted",
        ],
        "Rate Limits": [
            "rate_limit.updated",
            "rate_limit.deleted",
        ],
        "Authentication": [
            "login.succeeded",
            "login.failed",
            "logout.succeeded",
            "logout.failed",
        ],
        "Organization": [
            "organization.updated",
        ],
    }
    
    # Apply Major Section Header Style (80-character width)
    click.echo(f"\n{'='*80}")
    click.echo("Common Audit Log Event Types")
    click.echo(f"{'='*80}\n")
    
    # Apply Message Prefix Style ([INFO])
    click.echo("[INFO] Use these with --event-type option to filter logs\n")
    
    # Apply Lists and Bullet Points Style (3-space indentation)
    for category, types in event_types.items():
        click.echo(f"\n{category}:")
        for event_type in types:
            click.echo(f"   • {event_type}")
    
    # Apply Tips and Suggestions Style ([TIP] prefix and 3-space indentation for commands)
    click.echo("\n[TIP] Examples:")
    click.echo("   python openai_admin.py audit list --event-type=user.added --days=7")
    click.echo("   python openai_admin.py audit list --event-type=login.failed --days=1")
    click.echo("   python openai_admin.py audit list --actor-email=user@example.com --days=30\n")


if __name__ == '__main__':
    cli(obj={})