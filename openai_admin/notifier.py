"""Notification utilities for OpenAI Admin CLI"""
import os
import json
import requests
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
        config_path = Path(__file__).parent.parent / 'config' / 'mattermost.json'
        
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('users', {})
        except Exception as e:
            raise ValueError(f"Failed to load Mattermost config: {e}")
    
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
            user_id: Internal user ID (from mattermost.json)
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
    
    def is_available(self, channel: str) -> bool:
        """Check if a notification channel is available"""
        return channel in self.notifiers
    
    def send(self, channel: str, user_id: str, message: str) -> bool:
        """
        Send a notification
        
        Args:
            channel: Notification channel (e.g., 'mattermost')
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
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to send notification: {e}")
    
    def get_available_channels(self) -> list:
        """Get list of available notification channels"""
        return list(self.notifiers.keys())
