"""Utility functions for OpenAI Admin CLI"""
from typing import Optional
from datetime import datetime
import functools
import click
import io
import sys


def format_timestamp(ts: Optional[int]) -> str:
    """Format Unix timestamp to readable date"""
    if ts is None:
        return "N/A"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def format_redacted_value(value: str) -> str:
    """Format redacted API key value to be more compact"""
    if not value:
        return "N/A"
    # Replace long strings of asterisks (4 or more) with just 5 stars
    import re
    shortened = re.sub(r'\*{4,}', '*****', value)
    return shortened


def notification_options(func):
    """
    Decorator to add --notify and --channel options to a command.
    """
    func = click.option('--channel', type=click.Choice(['mattermost']), help='Notification channel (e.g., mattermost)')(func)
    func = click.option('--notify', help='User ID to notify (requires --channel)')(func)
    return func


def with_notification(func):
    """
    Decorator to add notification support to CLI commands.
    Captures command output and sends it via configured notification channel.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context()
        
        # Check for notification settings from command-level options first, then fall back to root-level
        notify_user = kwargs.pop('notify', None) or ctx.obj.get('notify_user')
        notify_channel = kwargs.pop('channel', None) or ctx.obj.get('notify_channel')
        
        # Validate notification options
        if notify_user and not notify_channel:
            click.echo("Error: --notify requires --channel", err=True)
            ctx.exit(1)
        if notify_channel and not notify_user:
            click.echo("Error: --channel requires --notify", err=True)
            ctx.exit(1)
        
        # If no notification is configured, just run the command normally
        if not notify_user or not notify_channel:
            return func(*args, **kwargs)
        
        # Capture output
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        captured_output = io.StringIO()
        
        try:
            # Redirect stdout and stderr to capture output
            sys.stdout = captured_output
            sys.stderr = captured_output
            
            # Run the command
            result = func(*args, **kwargs)
            success = True
            
        except Exception as e:
            # Capture errors
            captured_output.write(f"\nError: {str(e)}\n")
            success = False
            result = None
            
        finally:
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            # Get captured output
            output = captured_output.getvalue()
            
            # Print to console
            print(output, end='')
            
            # Send notification
            try:
                from openai_admin.notifier import NotificationManager
                
                notifier = NotificationManager()
                
                if not notifier.is_available(notify_channel):
                    click.echo(f"\n[WARNING] Notification channel '{notify_channel}' is not available", err=True)
                    return result
                
                # Get command name from context
                command_path = ctx.command_path
                
                # Format message
                if notify_channel == 'mattermost':
                    message = notifier.notifiers[notify_channel].format_command_output(
                        command_path,
                        output,
                        success
                    )
                else:
                    message = f"Command: {command_path}\n\nOutput:\n{output}"
                
                # Send notification
                notifier.send(notify_channel, notify_user, message)
                click.echo(f"\n[SUCCESS] Notification sent to user {notify_user} via {notify_channel}", err=True)
                
            except Exception as e:
                click.echo(f"\n[ERROR] Failed to send notification: {e}", err=True)
        
        return result
    
    return wrapper

