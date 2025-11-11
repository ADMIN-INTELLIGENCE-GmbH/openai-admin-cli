"""Notification testing and management commands"""
import click
import json
from openai_admin.notifier import NotificationManager


@click.group()
def notify():
    """Manage and test notifications"""
    pass


@notify.command('test')
@click.argument('user_id')
@click.option('--channel', type=click.Choice(['mattermost', 'email']), default='mattermost', help='Notification channel')
@click.option('--message', default='Test notification from OpenAI Admin CLI', help='Custom test message')
@click.pass_context
def test_notification(ctx, user_id, channel, message):
    """Test sending a notification to a user"""
    try:
        notifier = NotificationManager()
        
        if not notifier.is_available(channel):
            click.echo(f"[ERROR] Notification channel '{channel}' is not available or not configured", err=True)
            click.echo(f"Available channels: {', '.join(notifier.get_available_channels()) or 'none'}", err=True)
            return
        
        click.echo(f"[INFO] Sending test notification to user {user_id} via {channel}...")
        
        # Get user info
        if channel in ['mattermost', 'email']:
            channel_notifier = notifier.notifiers[channel]
            user_info = channel_notifier.get_user_info(user_id)
            if user_info:
                click.echo(f"[INFO] User: {user_info.get('name')} ({user_info.get('email')})")
        
        # Send notification
        notifier.send(channel, user_id, message)
        
        click.echo(f"[SUCCESS] Test notification sent successfully!")
        
    except Exception as e:
        click.echo(f"[ERROR] Failed to send test notification: {e}", err=True)


@notify.command('list-users')
@click.option('--channel', type=click.Choice(['mattermost', 'email']), help='Notification channel (optional, shows all if not specified)')
@click.pass_context
def list_users(ctx, channel):
    """List available users for notifications"""
    try:
        notifier = NotificationManager()
        
        channels_to_check = [channel] if channel else notifier.get_available_channels()
        
        if not channels_to_check:
            click.echo("[ERROR] No notification channels are available or configured", err=True)
            return
        
        for ch in channels_to_check:
            if not notifier.is_available(ch):
                click.echo(f"[WARNING] Channel '{ch}' is not available or not configured", err=True)
                continue
            
            ch_notifier = notifier.notifiers[ch]
            users = ch_notifier.user_mappings
            
            if not users:
                click.echo(f"[INFO] No users configured for {ch} notifications")
                continue
            
            click.echo(f"\n[INFO] Available users for {ch} notifications:\n")
            
            for user_id, user_info in sorted(users.items(), key=lambda x: int(x[0])):
                click.echo(f"  User ID: {user_id}")
                click.echo(f"    Name:  {user_info.get('name', 'N/A')}")
                click.echo(f"    Email: {user_info.get('email', 'N/A')}")
                if ch == 'mattermost':
                    click.echo(f"    MM User ID: {user_info.get('mattermost_user_id', 'N/A')}")
                    click.echo(f"    MM Channel ID: {user_info.get('mattermost_channel_id', 'N/A')}")
                click.echo()
            
            click.echo(f"Total: {len(users)} users configured for {ch}")
        
    except Exception as e:
        click.echo(f"[ERROR] Failed to list users: {e}", err=True)


@notify.command('status')
@click.pass_context
def notification_status(ctx):
    """Show notification system status"""
    try:
        notifier = NotificationManager()
        
        available_channels = notifier.get_available_channels()
        
        click.echo("\n[INFO] Notification System Status\n")
        
        if not available_channels:
            click.echo("[WARNING] No notification channels configured")
            click.echo("\nTo configure Mattermost notifications:")
            click.echo("  1. Set MATTERMOST_BOT_TOKEN in .env")
            click.echo("  2. Set MATTERMOST_BOT_ID in .env")
            click.echo("  3. Set MATTERMOST_BASE_URL in .env (optional)")
            click.echo("  4. Configure user mappings in config/users.json")
            click.echo("\nTo configure Email notifications:")
            click.echo("  1. Set MAIL_HOST in .env")
            click.echo("  2. Set MAIL_USERNAME in .env")
            click.echo("  3. Set MAIL_PASSWORD in .env")
            click.echo("  4. Set MAIL_PORT in .env (optional, default: 587)")
            click.echo("  5. Configure user mappings in config/users.json")
            return
        
        click.echo(f"Available channels: {', '.join(available_channels)}")
        
        for channel in available_channels:
            click.echo(f"\n{channel.upper()} Configuration:")
            
            if channel == 'mattermost':
                mm_notifier = notifier.notifiers['mattermost']
                click.echo(f"  Base URL: {mm_notifier.base_url}")
                click.echo(f"  Bot ID: {mm_notifier.bot_id}")
                click.echo(f"  Configured users: {len(mm_notifier.user_mappings)}")
            elif channel == 'email':
                email_notifier = notifier.notifiers['email']
                click.echo(f"  Host: {email_notifier.host}")
                click.echo(f"  Port: {email_notifier.port}")
                click.echo(f"  From: {email_notifier.from_name} <{email_notifier.from_email}>")
                click.echo(f"  Configured users: {len(email_notifier.user_mappings)}")
        
        click.echo("\n[SUCCESS] Notification system is ready")
        
    except Exception as e:
        click.echo(f"[ERROR] Failed to check status: {e}", err=True)
