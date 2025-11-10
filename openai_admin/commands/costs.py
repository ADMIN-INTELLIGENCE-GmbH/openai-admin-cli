import click
import json
import sys
from datetime import datetime, timedelta
from tabulate import tabulate
from openai_admin.utils import format_timestamp, format_redacted_value
import requests

@click.command('costs')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD), defaults to now')
@click.option('--days', type=int, help='Alternative: number of days to look back from now')
@click.option('--group-by', multiple=True, type=click.Choice(['project_id', 'line_item']), 
              help='Group results by field (can be used multiple times)')
@click.option('--project-id', multiple=True, help='Filter by project ID (can be used multiple times)')
@click.option('--limit', default=7, help='Number of time buckets to return')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
def costs_command(ctx, start_date, end_date, days, group_by, project_id, limit, output_format):
    """Get costs/spending data"""
    client = ctx.obj['client']
    
    from datetime import datetime, timedelta
    
    # Validate that either --days or --start-date is provided
    if not days and not start_date:
        click.echo("[ERROR] Either --days or --start-date must be provided", err=True)
        return
    
    start_time = None
    end_time = None
    
    if days:
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days)
        start_time = int(start_dt.timestamp())
        end_time = int(end_dt.timestamp())
    else:
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
    
    # Apply Progress Message Style
    click.echo("Fetching costs data...")
    result = client.get_costs(
        start_time=start_time,
        end_time=end_time,
        group_by=list(group_by) if group_by else None,
        limit=limit,
        project_ids=list(project_id) if project_id else None
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
        click.echo("No cost data found for the specified period.")
        return
    
    # Apply Major Section Header Style
    start_date_formatted = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d')
    end_date_formatted = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d')
    click.echo(f"\n{'='*80}")
    click.echo(f"Costs Report")
    click.echo(f"Period: {start_date_formatted} to {end_date_formatted}")
    click.echo(f"{'='*80}\n")
    
    total_cost = 0.0
    
    for bucket in data_buckets:
        # Format timestamps consistently: YYYY-MM-DD HH:MM:SS
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
        bucket_total = 0.0
        
        for result_item in results:
            row = []
            
            # Add grouping columns if specified
            if 'project_id' in group_by:
                row.append(result_item.get('project_id') or 'N/A')
            if 'line_item' in group_by:
                # Apply Table Header Style (Title Case)
                row.append(result_item.get('line_item') or 'N/A')
            
            # Add cost
            amount = result_item.get('amount', {})
            value = amount.get('value', 0)
            currency = amount.get('currency', 'usd').upper()
            
            bucket_total += value
            total_cost += value
            
            # Apply Monetary Values Format (with thousand separators for large amounts, although not needed for this small example, the format is consistent)
            formatted_cost = f"${value:,.4f} {currency}" 
            row.append(formatted_cost)
            
            table_data.append(row)
        
        # Build headers (Title Case)
        headers = []
        if 'project_id' in group_by:
            headers.append('Project ID')
        if 'line_item' in group_by:
            headers.append('Line Item')
        headers.append('Cost')
        
        # Apply Table Output Style (grid format)
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        # Apply Monetary Values Format for Bucket Total
        bucket_total_formatted = f"${bucket_total:,.4f}"
        click.echo(f"\nBucket Total: {bucket_total_formatted}")
        click.echo()
    
    # Apply Major Section Header Style and Monetary Values Format for TOTAL COST
    total_cost_formatted = f"${total_cost:,.4f}"
    click.echo(f"{'='*80}")
    click.echo(f"TOTAL COST: {total_cost_formatted}")
    click.echo(f"{'='*80}\n")