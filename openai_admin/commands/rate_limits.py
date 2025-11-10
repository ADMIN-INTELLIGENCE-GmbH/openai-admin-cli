"""Rate Limits commands"""
import click
import json
import sys
from datetime import datetime, timedelta
from tabulate import tabulate
from openai_admin.utils import format_timestamp, format_redacted_value
import requests

@click.group(name='rate-limits')
def rate_limits():
    """Manage project rate limits"""
    pass


@rate_limits.command('list')
@click.argument('project_id')
@click.option('--limit', default=100, help='Maximum number of rate limits to return')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
def list_rate_limits(ctx, project_id, limit, output_format):
    """List all rate limits for a project"""
    client = ctx.obj['client']
    
    # Apply Progress Message Style
    click.echo(f"Fetching rate limits for project {project_id}...")
    result = client.list_project_rate_limits(project_id, limit=limit)
    
    limits_data = result.get('data', [])
    
    if not limits_data:
        # Apply Empty Results Style
        click.echo("No rate limits found for this project.")
        return
    
    if output_format == 'json':
        import json
        # Apply JSON Output Style
        click.echo(json.dumps(result, indent=2))
    else:
        # Table format
        table_data = []
        for rl in limits_data:
            # Build a compact display of limits with thousand separators
            limits_str = []
            if rl.get('max_requests_per_1_minute'):
                limits_str.append(f"Req/min: {rl.get('max_requests_per_1_minute'):,}")
            if rl.get('max_tokens_per_1_minute'):
                limits_str.append(f"Tokens/min: {rl.get('max_tokens_per_1_minute'):,}")
            if rl.get('max_images_per_1_minute'):
                limits_str.append(f"Img/min: {rl.get('max_images_per_1_minute'):,}")
            if rl.get('max_audio_megabytes_per_1_minute'):
                limits_str.append(f"Audio MB/min: {rl.get('max_audio_megabytes_per_1_minute'):,}")
            if rl.get('max_requests_per_1_day'):
                limits_str.append(f"Req/day: {rl.get('max_requests_per_1_day'):,}")
            if rl.get('batch_1_day_max_input_tokens'):
                limits_str.append(f"Batch tokens/day: {rl.get('batch_1_day_max_input_tokens'):,}")
            
            # Apply Long Text Truncation for ID
            rl_id_truncated = rl.get('id', '')[:20] + '...' if rl.get('id') else 'N/A'
            
            table_data.append([
                rl_id_truncated,
                rl.get('model', 'N/A'),
                '\n'.join(limits_str) if limits_str else 'N/A'
            ])
        
        # Apply Table Header Style (Title Case)
        headers = ['ID', 'Model', 'Limits']
        
        # Apply Summary Lines Style
        click.echo(f"\nTotal rate limits: {len(limits_data)}\n")
        
        # Apply Table Output Style (grid format)
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))


@rate_limits.command('update')
@click.argument('project_id')
@click.argument('rate_limit_id')
@click.option('--max-requests-per-minute', type=int, help='Maximum requests per minute')
@click.option('--max-tokens-per-minute', type=int, help='Maximum tokens per minute')
@click.option('--max-images-per-minute', type=int, help='Maximum images per minute')
@click.option('--max-audio-mb-per-minute', type=int, help='Maximum audio megabytes per minute')
@click.option('--max-requests-per-day', type=int, help='Maximum requests per day')
@click.option('--batch-max-tokens-per-day', type=int, help='Maximum batch input tokens per day')
@click.pass_context
def update_rate_limit(ctx, project_id, rate_limit_id, max_requests_per_minute, 
                     max_tokens_per_minute, max_images_per_minute, max_audio_mb_per_minute,
                     max_requests_per_day, batch_max_tokens_per_day):
    """Update rate limit settings for a model
    
    Only provide the limits you want to change. Omitted limits will remain unchanged.
    """
    client = ctx.obj['client']
    
    # Indentation level for lists
    indent_1 = ' ' * 3

    # Build the update payload
    updates = {}
    if max_requests_per_minute is not None:
        updates['max_requests_per_1_minute'] = max_requests_per_minute
    if max_tokens_per_minute is not None:
        updates['max_tokens_per_1_minute'] = max_tokens_per_minute
    if max_images_per_minute is not None:
        updates['max_images_per_1_minute'] = max_images_per_minute
    if max_audio_mb_per_minute is not None:
        updates['max_audio_megabytes_per_1_minute'] = max_audio_mb_per_minute
    if max_requests_per_day is not None:
        updates['max_requests_per_1_day'] = max_requests_per_day
    if batch_max_tokens_per_day is not None:
        updates['batch_1_day_max_input_tokens'] = batch_max_tokens_per_day
    
    if not updates:
        click.echo("[ERROR] No updates specified. Use --help to see available options.", err=True)
        sys.exit(1)
    
    # Show proposed changes (Preview)
    # Apply Progress Message Style
    click.echo(f"Fetching current rate limit settings for {rate_limit_id}...")
    try:
        current_rl = client.get_project_rate_limit(project_id, rate_limit_id)
        model_name = current_rl.get('model', 'N/A')
    except Exception as e:
        click.echo(f"[ERROR] Failed to fetch rate limit {rate_limit_id}: {e}", err=True)
        sys.exit(1)

    # Apply Update Commands Structure
    click.echo(f"\n[INFO] Proposed changes for Model '{model_name}' ({rate_limit_id}):")
    
    # Apply Lists and Bullet Points Style
    for key, value in updates.items():
        # Make the key more readable
        readable_key = key.replace('_', ' ').replace('1', '').title().strip()
        # Use thousand separators
        click.echo(f"{indent_1}• {readable_key}: {value:,}")
    
    # Apply Confirmation Prompts Style
    click.echo()
    if not click.confirm('Do you want to apply these changes?'):
        click.echo("Cancelled.")
        return
    
    # Update the rate limit (Progress Update)
    click.echo(f"\n[INFO] Applying changes...")
    try:
        result = client.update_project_rate_limit(project_id, rate_limit_id, **updates)
        
        # Apply Success Prefix Style
        click.echo(f"\n[SUCCESS] Rate limit updated successfully!")
        
        # Show updated values
        click.echo(f"\n[INFO] Updated limits for {result.get('model')}:")
        
        # Apply consistent formatting for updated values with labels and thousand separators
        if result.get('max_requests_per_1_minute') is not None:
            click.echo(f"{indent_1}Max Requests/min: {result.get('max_requests_per_1_minute'):,}")
        if result.get('max_tokens_per_1_minute') is not None:
            click.echo(f"{indent_1}Max Tokens/min:   {result.get('max_tokens_per_1_minute'):,}")
        if result.get('max_images_per_1_minute') is not None:
            click.echo(f"{indent_1}Max Images/min:   {result.get('max_images_per_1_minute'):,}")
        if result.get('max_audio_megabytes_per_1_minute') is not None:
            click.echo(f"{indent_1}Max Audio MB/min: {result.get('max_audio_megabytes_per_1_minute'):,}")
        if result.get('max_requests_per_1_day') is not None:
            click.echo(f"{indent_1}Max Requests/day: {result.get('max_requests_per_1_day'):,}")
        if result.get('batch_1_day_max_input_tokens') is not None:
            click.echo(f"{indent_1}Max Batch tokens/day: {result.get('batch_1_day_max_input_tokens'):,}")
        
    except Exception as e:
        # Apply Detailed Errors with Context Style
        click.echo(f"\n[ERROR] Error updating rate limit {rate_limit_id}: {e}", err=True)
        sys.exit(1)