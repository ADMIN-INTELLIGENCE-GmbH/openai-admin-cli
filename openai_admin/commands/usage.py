"""Usage commands"""
import click
import json
import sys
from datetime import datetime, timedelta
from tabulate import tabulate
from openai_admin.utils import format_timestamp, format_redacted_value, with_notification, notification_options
import requests

@click.group()
def usage():
    """View usage analytics"""
    pass


@usage.command('completions')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD), defaults to now')
@click.option('--days', type=int, help='Alternative: number of days to look back from now')
@click.option('--group-by', multiple=True, type=click.Choice(['project_id', 'user_id', 'api_key_id', 'model', 'batch', 'service_tier']), 
              help='Group results by field (can be used multiple times)')
@click.option('--project-id', multiple=True, help='Filter by project ID (can be used multiple times)')
@click.option('--model', multiple=True, help='Filter by model (can be used multiple times)')
@click.option('--limit', default=7, help='Number of time buckets to return')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
@notification_options
@with_notification
def usage_completions(ctx, start_date, end_date, days, group_by, project_id, model, limit, output_format):
    """Get completions (chat/text) usage statistics"""
    client = ctx.obj['client']
    
    # Handle date conversion
    from datetime import datetime, timedelta
    
    start_time = None
    end_time = None
    
    if days:
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days)
        start_time = int(start_dt.timestamp())
        end_time = int(end_dt.timestamp())
    elif start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            start_time = int(start_dt.timestamp())
            
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                end_time = int(end_dt.timestamp())
            else:
                end_time = int(datetime.now().timestamp())
        except ValueError as e:
            # Apply Error Message Style
            click.echo(f"[ERROR] Error parsing date: {e}", err=True)
            click.echo("Use format: YYYY-MM-DD", err=True)
            return
    else:
        # Apply Error Message Style
        click.echo("[ERROR] Either --start-date or --days must be provided", err=True)
        sys.exit(1)
    
    # Apply Progress Message Style
    click.echo("Fetching completions usage data...")
    result = client.get_usage_completions(
        start_time=start_time,
        end_time=end_time,
        group_by=list(group_by) if group_by else None,
        limit=limit,
        project_ids=list(project_id) if project_id else None,
        models=list(model) if model else None
    )
    
    if output_format == 'json':
        import json
        # Apply JSON Output Style
        click.echo(json.dumps(result, indent=2))
        return
    
    # Table format
    data_buckets = result.get('data', [])
    
    if not data_buckets:
        # Apply Empty Results Style
        click.echo("No usage data found for the specified period.")
        return
    
    # Apply Major Section Header Style
    start_date_formatted = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d')
    end_date_formatted = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d')
    click.echo(f"\n{'='*80}")
    click.echo(f"Completions Usage Report")
    click.echo(f"Period: {start_date_formatted} to {end_date_formatted}")
    click.echo(f"{'='*80}\n")
    
    for bucket in data_buckets:
        # Apply Consistent Timestamp Formatting
        bucket_start = format_timestamp(bucket.get('start_time'))
        bucket_end = format_timestamp(bucket.get('end_time'))
        
        # Apply Subsection Header Style (Minor Separator)
        click.echo(f"{'────────────────────────────────────────────────────────────────────────────────'}")
        click.echo(f"Time Bucket: {bucket_start} to {bucket_end}")
        click.echo(f"{'────────────────────────────────────────────────────────────────────────────────'}")
        
        results = bucket.get('results', [])
        if not results:
            # Apply Indentation (Level 1: 3 spaces) for minor message
            click.echo("   No data in this bucket.\n")
            continue
        
        table_data = []
        for result_item in results:
            row = []
            
            # Add grouping columns if specified
            if 'project_id' in group_by:
                project_id_val = result_item.get('project_id', 'N/A')
                row.append(project_id_val)
            if 'model' in group_by:
                row.append(result_item.get('model') or 'N/A')
            if 'user_id' in group_by:
                user_id_val = result_item.get('user_id', 'N/A')
                row.append(user_id_val)
            if 'api_key_id' in group_by:
                api_key_id_val = result_item.get('api_key_id', 'N/A')
                row.append(api_key_id_val)
            if 'batch' in group_by:
                row.append('Yes' if result_item.get('batch') else 'No')
            if 'service_tier' in group_by:
                row.append(result_item.get('service_tier') or 'N/A')
            
            # Add usage metrics (with thousand separators)
            row.extend([
                f"{result_item.get('input_tokens', 0):,}",
                f"{result_item.get('output_tokens', 0):,}",
                f"{result_item.get('input_cached_tokens', 0):,}",
                f"{result_item.get('num_model_requests', 0):,}"
            ])
            
            table_data.append(row)
        
        # Build headers (Title Case)
        headers = []
        if 'project_id' in group_by:
            headers.append('Project ID')
        if 'model' in group_by:
            headers.append('Model')
        if 'user_id' in group_by:
            headers.append('User ID')
        if 'api_key_id' in group_by:
            headers.append('API Key ID')
        if 'batch' in group_by:
            headers.append('Batch')
        if 'service_tier' in group_by:
            headers.append('Service Tier')
        
        headers.extend(['Input Tokens', 'Output Tokens', 'Cached Tokens', 'Requests'])
        
        # Apply Table Output Style (grid format)
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo()


@usage.command('embeddings')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD), defaults to now')
@click.option('--days', type=int, help='Alternative: number of days to look back from now')
@click.option('--group-by', multiple=True, type=click.Choice(['project_id', 'user_id', 'api_key_id', 'model']), 
              help='Group results by field')
@click.option('--limit', default=7, help='Number of time buckets to return')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
@notification_options
@with_notification
def usage_embeddings(ctx, start_date, end_date, days, group_by, limit, output_format):
    """Get embeddings usage statistics"""
    client = ctx.obj['client']
    
    from datetime import datetime, timedelta
    
    start_time = None
    end_time = None
    
    if days:
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days)
        start_time = int(start_dt.timestamp())
        end_time = int(end_dt.timestamp())
    elif start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            start_time = int(start_dt.timestamp())
            end_time = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()) if end_date else int(datetime.now().timestamp())
        except ValueError as e:
            # Apply Error Message Style
            click.echo(f"[ERROR] Error parsing date: {e}", err=True)
            click.echo("Use format: YYYY-MM-DD", err=True)
            return
    else:
        # Apply Error Message Style
        click.echo("[ERROR] Either --start-date or --days must be provided", err=True)
        sys.exit(1)
    
    # Apply Progress Message Style
    click.echo("Fetching embeddings usage data...")
    result = client.get_usage_embeddings(
        start_time=start_time,
        end_time=end_time,
        group_by=list(group_by) if group_by else None,
        limit=limit
    )
    
    if output_format == 'json':
        import json
        # Apply JSON Output Style
        click.echo(json.dumps(result, indent=2))
        return
    
    data_buckets = result.get('data', [])
    if not data_buckets:
        # Apply Empty Results Style
        click.echo("No usage data found for the specified period.")
        return
    
    # Apply Major Section Header Style
    click.echo(f"\n{'='*80}")
    click.echo(f"Embeddings Usage Report")
    click.echo(f"{'='*80}\n")
    
    for bucket in data_buckets:
        # Apply Consistent Timestamp Formatting
        bucket_start = format_timestamp(bucket.get('start_time'))
        bucket_end = format_timestamp(bucket.get('end_time'))
        
        # Apply Subsection Header Style (Minor Separator)
        click.echo(f"{'────────────────────────────────────────────────────────────────────────────────'}")
        click.echo(f"Time Bucket: {bucket_start} to {bucket_end}")
        click.echo(f"{'────────────────────────────────────────────────────────────────────────────────'}")
        
        table_data = []
        for result_item in bucket.get('results', []):
            row = []
            if 'project_id' in group_by:
                project_id_val = result_item.get('project_id', 'N/A')
                row.append(project_id_val)
            if 'model' in group_by:
                row.append(result_item.get('model') or 'N/A')
            if 'user_id' in group_by:
                user_id_val = result_item.get('user_id', 'N/A')
                row.append(user_id_val)
            if 'api_key_id' in group_by:
                api_key_id_val = result_item.get('api_key_id', 'N/A')
                row.append(api_key_id_val)

            # Add usage metrics (with thousand separators)
            row.extend([
                f"{result_item.get('input_tokens', 0):,}",
                f"{result_item.get('num_model_requests', 0):,}"
            ])
            table_data.append(row)
        
        # Build headers (Title Case)
        headers = []
        if 'project_id' in group_by:
            headers.append('Project ID')
        if 'model' in group_by:
            headers.append('Model')
        if 'user_id' in group_by:
            headers.append('User ID')
        if 'api_key_id' in group_by:
            headers.append('API Key ID')
        headers.extend(['Input Tokens', 'Requests'])
        
        # Apply Table Output Style (grid format)
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo()


@usage.command('images')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD), defaults to now')
@click.option('--days', type=int, help='Alternative: number of days to look back from now')
@click.option('--group-by', multiple=True, type=click.Choice(['project_id', 'model', 'size', 'source']), 
              help='Group results by field')
@click.option('--limit', default=7, help='Number of time buckets to return')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
@notification_options
@with_notification
def usage_images(ctx, start_date, end_date, days, group_by, limit, output_format):
    """Get image generation usage statistics"""
    client = ctx.obj['client']
    
    from datetime import datetime, timedelta
    
    start_time = None
    end_time = None
    
    if days:
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days)
        start_time = int(start_dt.timestamp())
        end_time = int(end_dt.timestamp())
    elif start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            start_time = int(start_dt.timestamp())
            end_time = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()) if end_date else int(datetime.now().timestamp())
        except ValueError as e:
            # Apply Error Message Style
            click.echo(f"[ERROR] Error parsing date: {e}", err=True)
            click.echo("Use format: YYYY-MM-DD", err=True)
            return
    else:
        # Apply Error Message Style
        click.echo("[ERROR] Either --start-date or --days must be provided", err=True)
        sys.exit(1)
    
    # Apply Progress Message Style
    click.echo("Fetching images usage data...")
    result = client.get_usage_images(
        start_time=start_time,
        end_time=end_time,
        group_by=list(group_by) if group_by else None,
        limit=limit
    )
    
    if output_format == 'json':
        import json
        # Apply JSON Output Style
        click.echo(json.dumps(result, indent=2))
        return
    
    data_buckets = result.get('data', [])
    if not data_buckets:
        # Apply Empty Results Style
        click.echo("No usage data found for the specified period.")
        return
    
    # Apply Major Section Header Style
    click.echo(f"\n{'='*80}")
    click.echo(f"Images Usage Report")
    click.echo(f"{'='*80}\n")
    
    for bucket in data_buckets:
        # Apply Consistent Timestamp Formatting
        bucket_start = format_timestamp(bucket.get('start_time'))
        bucket_end = format_timestamp(bucket.get('end_time'))

        # Apply Subsection Header Style (Minor Separator)
        click.echo(f"{'────────────────────────────────────────────────────────────────────────────────'}")
        click.echo(f"Time Bucket: {bucket_start} to {bucket_end}")
        click.echo(f"{'────────────────────────────────────────────────────────────────────────────────'}")
        
        table_data = []
        for result_item in bucket.get('results', []):
            row = []
            if 'project_id' in group_by:
                project_id_val = result_item.get('project_id', 'N/A')
                row.append(project_id_val)
            if 'model' in group_by:
                row.append(result_item.get('model') or 'N/A')
            if 'size' in group_by:
                row.append(result_item.get('size') or 'N/A')
            if 'source' in group_by:
                row.append(result_item.get('source') or 'N/A')
            
            # Add usage metrics (with thousand separators)
            row.extend([
                f"{result_item.get('images', 0):,}",
                f"{result_item.get('num_model_requests', 0):,}"
            ])
            table_data.append(row)
        
        # Build headers (Title Case)
        headers = []
        if 'project_id' in group_by:
            headers.append('Project ID')
        if 'model' in group_by:
            headers.append('Model')
        if 'size' in group_by:
            headers.append('Size')
        if 'source' in group_by:
            headers.append('Source')
        headers.extend(['Images', 'Requests'])
        
        # Apply Table Output Style (grid format)
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo()


@usage.command('audio-speeches')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD), defaults to now') # Added missing end-date option
@click.option('--days', type=int, help='Alternative: number of days to look back from now')
@click.option('--group-by', multiple=True, type=click.Choice(['project_id', 'model']), help='Group results by field')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
@notification_options
@with_notification
def usage_audio_speeches(ctx, start_date, end_date, days, group_by, output_format): # Added end_date to func signature
    """Get audio speeches (TTS) usage statistics"""
    client = ctx.obj['client']
    
    from datetime import datetime, timedelta
    
    start_time = None
    end_time = None
    
    if days:
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days)
        start_time = int(start_dt.timestamp())
        end_time = int(end_dt.timestamp())
    elif start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            start_time = int(start_dt.timestamp())
            end_time = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()) if end_date else int(datetime.now().timestamp()) # Corrected end_time logic
        except ValueError as e:
            # Apply Error Message Style
            click.echo(f"[ERROR] Error parsing date: {e}", err=True)
            click.echo("Use format: YYYY-MM-DD", err=True)
            return
    else:
        # Apply Error Message Style
        click.echo("[ERROR] Either --start-date or --days must be provided", err=True)
        sys.exit(1)
    
    # Apply Progress Message Style
    click.echo("Fetching audio speeches usage data...")
    result = client.get_usage_audio_speeches(
        start_time=start_time,
        end_time=end_time,
        group_by=list(group_by) if group_by else None
    )
    
    if output_format == 'json':
        import json
        # Apply JSON Output Style
        click.echo(json.dumps(result, indent=2))
        return
    
    data_buckets = result.get('data', [])
    if not data_buckets:
        # Apply Empty Results Style
        click.echo("No usage data found for the specified period.")
        return
    
    # Apply Major Section Header Style
    click.echo(f"\n{'='*80}")
    click.echo(f"Audio Speeches (TTS) Usage Report")
    click.echo(f"{'='*80}\n")
    
    for bucket in data_buckets:
        # Apply Consistent Timestamp Formatting
        bucket_start = format_timestamp(bucket.get('start_time'))
        bucket_end = format_timestamp(bucket.get('end_time'))

        # Apply Subsection Header Style (Minor Separator)
        click.echo(f"{'────────────────────────────────────────────────────────────────────────────────'}")
        click.echo(f"Time Bucket: {bucket_start} to {bucket_end}")
        click.echo(f"{'────────────────────────────────────────────────────────────────────────────────'}")
        
        table_data = []
        for result_item in bucket.get('results', []):
            row = []
            if 'project_id' in group_by:
                project_id_val = result_item.get('project_id', 'N/A')
                row.append(project_id_val)
            if 'model' in group_by:
                row.append(result_item.get('model') or 'N/A')
            
            # Add usage metrics (with thousand separators)
            row.extend([
                f"{result_item.get('characters', 0):,}",
                f"{result_item.get('num_model_requests', 0):,}"
            ])
            table_data.append(row)
        
        # Build headers (Title Case)
        headers = []
        if 'project_id' in group_by:
            headers.append('Project ID')
        if 'model' in group_by:
            headers.append('Model')
        headers.extend(['Characters', 'Requests'])
        
        # Apply Table Output Style (grid format)
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo()


@usage.command('audio-transcriptions')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD), defaults to now') # Added missing end-date option
@click.option('--days', type=int, help='Alternative: number of days to look back from now')
@click.option('--group-by', multiple=True, type=click.Choice(['project_id', 'model']), help='Group results by field')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
@notification_options
@with_notification
def usage_audio_transcriptions(ctx, start_date, end_date, days, group_by, output_format): # Added end_date to func signature
    """Get audio transcriptions (Whisper) usage statistics"""
    client = ctx.obj['client']
    
    from datetime import datetime, timedelta
    
    start_time = None
    end_time = None
    
    if days:
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days)
        start_time = int(start_dt.timestamp())
        end_time = int(end_dt.timestamp())
    elif start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            start_time = int(start_dt.timestamp())
            end_time = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp()) if end_date else int(datetime.now().timestamp()) # Corrected end_time logic
        except ValueError as e:
            # Apply Error Message Style
            click.echo(f"[ERROR] Error parsing date: {e}", err=True)
            click.echo("Use format: YYYY-MM-DD", err=True)
            return
    else:
        # Apply Error Message Style
        click.echo("[ERROR] Either --start-date or --days must be provided", err=True)
        sys.exit(1)
    
    # Apply Progress Message Style
    click.echo("Fetching audio transcriptions usage data...")
    result = client.get_usage_audio_transcriptions(
        start_time=start_time,
        end_time=end_time,
        group_by=list(group_by) if group_by else None
    )
    
    if output_format == 'json':
        import json
        # Apply JSON Output Style
        click.echo(json.dumps(result, indent=2))
        return
    
    data_buckets = result.get('data', [])
    if not data_buckets:
        # Apply Empty Results Style
        click.echo("No usage data found for the specified period.")
        return
    
    # Apply Major Section Header Style
    click.echo(f"\n{'='*80}")
    click.echo(f"Audio Transcriptions (Whisper) Usage Report")
    click.echo(f"{'='*80}\n")
    
    for bucket in data_buckets:
        # Apply Consistent Timestamp Formatting
        bucket_start = format_timestamp(bucket.get('start_time'))
        bucket_end = format_timestamp(bucket.get('end_time'))

        # Apply Subsection Header Style (Minor Separator)
        click.echo(f"{'────────────────────────────────────────────────────────────────────────────────'}")
        click.echo(f"Time Bucket: {bucket_start} to {bucket_end}")
        click.echo(f"{'────────────────────────────────────────────────────────────────────────────────'}")
        
        table_data = []
        for result_item in bucket.get('results', []):
            row = []
            if 'project_id' in group_by:
                project_id_val = result_item.get('project_id', 'N/A')
                row.append(project_id_val)
            if 'model' in group_by:
                row.append(result_item.get('model') or 'N/A')
            
            # Add usage metrics (with thousand separators)
            row.extend([
                f"{result_item.get('seconds', 0):,}",
                f"{result_item.get('num_model_requests', 0):,}"
            ])
            table_data.append(row)
        
        # Build headers (Title Case)
        headers = []
        if 'project_id' in group_by:
            headers.append('Project ID')
        if 'model' in group_by:
            headers.append('Model')
        headers.extend(['Seconds', 'Requests'])
        
        # Apply Table Output Style (grid format)
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo()