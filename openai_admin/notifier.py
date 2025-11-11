"""Notification utilities for OpenAI Admin CLI"""
import os
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from pathlib import Path


class MattermostNotifier:
    """Send notifications via Mattermost"""
    
    def __init__(self):
        """Initialize Mattermost notifier with environment variables"""
        self.bot_token = os.getenv('MATTERMOST_BOT_TOKEN')
        self.bot_id = os.getenv('MATTERMOST_BOT_ID')
        self.base_url = os.getenv('MATTERMOST_BASE_URL', 'https://chat.admin-intelligence.de/api/v4')
        
        if not self.bot_token:
            raise ValueError("MATTERMOST_BOT_TOKEN environment variable is required")
        if not self.bot_id:
            raise ValueError("MATTERMOST_BOT_ID environment variable is required")
        
        self.headers = {
            'Authorization': f'Bearer {self.bot_token}',
            'Content-Type': 'application/json'
        }
        
        # Load user mappings
        self.user_mappings = self._load_user_mappings()
    
    def _load_user_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load user ID to Mattermost mappings from config file"""
        config_path = Path(__file__).parent.parent / 'config' / 'users.json'
        
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('users', {})
        except Exception as e:
            raise ValueError(f"Failed to load user config: {e}")
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information by user ID"""
        return self.user_mappings.get(str(user_id))
    
    def send_message(self, channel_id: str, message: str) -> Dict[str, Any]:
        """
        Send a direct message to a Mattermost channel
        
        Args:
            channel_id: Mattermost channel ID
            message: Message text to send
            
        Returns:
            API response data
        """
        response = requests.post(
            f"{self.base_url}/posts",
            headers=self.headers,
            json={
                'channel_id': channel_id,
                'message': message
            }
        )
        response.raise_for_status()
        return response.json()
    
    def send_to_user(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Send a message to a user by their user ID
        
        Args:
            user_id: Internal user ID (from users.json)
            message: Message text to send
            
        Returns:
            API response data
        """
        user_info = self.get_user_info(user_id)
        if not user_info:
            raise ValueError(f"User ID {user_id} not found in Mattermost mappings")
        
        channel_id = user_info.get('mattermost_channel_id')
        if not channel_id:
            raise ValueError(f"No Mattermost channel ID found for user {user_id}")
        
        return self.send_message(channel_id, message)
    
    def create_direct_channel(self, mattermost_user_id: str) -> str:
        """
        Create or get a direct channel with a user
        
        Args:
            mattermost_user_id: Mattermost user ID
            
        Returns:
            Channel ID
        """
        response = requests.post(
            f"{self.base_url}/channels/direct",
            headers=self.headers,
            json=[self.bot_id, mattermost_user_id]
        )
        response.raise_for_status()
        return response.json().get('id')
    
    def format_command_output(self, command: str, output: str, success: bool = True) -> str:
        """
        Format command output for Mattermost
        
        Args:
            command: Command that was executed
            output: Output from the command
            success: Whether the command succeeded
            
        Returns:
            Formatted message
        """
        status_emoji = "✅" if success else "❌"
        status_text = "Success" if success else "Failed"
        
        message = f"{status_emoji} **OpenAI Admin CLI - {status_text}**\n\n"
        message += f"**Command:** `{command}`\n\n"
        message += f"**Output:**\n```\n{output}\n```"
        
        return message


class EmailNotifier:
    """Send notifications via Email"""
    
    def __init__(self):
        """Initialize Email notifier with environment variables"""
        self.mailer = os.getenv('MAIL_MAILER', 'smtp')
        self.host = os.getenv('MAIL_HOST')
        self.port = int(os.getenv('MAIL_PORT', '587'))
        self.username = os.getenv('MAIL_USERNAME')
        self.password = os.getenv('MAIL_PASSWORD')
        self.from_email = os.getenv('MAIL_FROM_ADDRESS', self.username)
        self.from_name = os.getenv('MAIL_FROM_NAME', 'OpenAI Admin CLI')
        
        if not self.host:
            raise ValueError("MAIL_HOST environment variable is required")
        if not self.username:
            raise ValueError("MAIL_USERNAME environment variable is required")
        if not self.password:
            raise ValueError("MAIL_PASSWORD environment variable is required")
        
        # Load user mappings
        self.user_mappings = self._load_user_mappings()
    
    def _load_user_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load user ID to email mappings from config file"""
        config_path = Path(__file__).parent.parent / 'config' / 'users.json'
        
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('users', {})
        except Exception as e:
            raise ValueError(f"Failed to load user config: {e}")
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information by user ID"""
        return self.user_mappings.get(str(user_id))
    
    def send_email(self, to_email: str, subject: str, body: str, html: bool = False) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            html: Whether the body is HTML
            
        Returns:
            True if successful
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach body
            mime_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, mime_type))
            
            # Send email
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to send email: {e}")
    
    def send_to_user(self, user_id: str, message: str) -> bool:
        """
        Send an email to a user by their user ID
        
        Args:
            user_id: Internal user ID (from users.json)
            message: Message text to send
            
        Returns:
            True if successful
        """
        user_info = self.get_user_info(user_id)
        if not user_info:
            raise ValueError(f"User ID {user_id} not found in user mappings")
        
        email = user_info.get('email')
        if not email:
            raise ValueError(f"No email address found for user {user_id}")
        
        name = user_info.get('name', 'User')
        subject = "OpenAI Admin CLI - Command Output"
        
        return self.send_email(email, subject, message)
    
    def format_command_output(self, command: str, output: str, success: bool = True) -> str:
        """
        Format command output for email
        
        Args:
            command: Command that was executed
            output: Output from the command
            success: Whether the command succeeded
            
        Returns:
            Formatted message
        """
        status_text = "Success" if success else "Failed"
        
        message = f"OpenAI Admin CLI - {status_text}\n\n"
        message += f"Command: {command}\n\n"
        message += f"Output:\n{'-' * 50}\n{output}\n{'-' * 50}"
        
        return message


class NotificationManager:
    """Manage notifications across different channels"""
    
    def __init__(self):
        """Initialize notification manager"""
        self.notifiers = {}
        
        # Initialize available notifiers
        try:
            self.notifiers['mattermost'] = MattermostNotifier()
        except ValueError as e:
            # Mattermost not configured
            pass
        
        try:
            self.notifiers['email'] = EmailNotifier()
        except ValueError as e:
            # Email not configured
            pass
    
    def is_available(self, channel: str) -> bool:
        """Check if a notification channel is available"""
        return channel in self.notifiers
    
    def send(self, channel: str, user_id: str, message: str) -> bool:
        """
        Send a notification
        
        Args:
            channel: Notification channel (e.g., 'mattermost', 'email')
            user_id: User ID to notify
            message: Message to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available(channel):
            raise ValueError(f"Notification channel '{channel}' is not available or not configured")
        
        notifier = self.notifiers[channel]
        
        try:
            if channel == 'mattermost':
                notifier.send_to_user(user_id, message)
            elif channel == 'email':
                notifier.send_to_user(user_id, message)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to send notification: {e}")
    
    def get_available_channels(self) -> list:
        """Get list of available notification channels"""
        return list(self.notifiers.keys())
