"""OpenAI Admin API Client"""
import os
import sys
import logging
from typing import Optional, List
import click
import requests

logger = logging.getLogger('openai_admin')


class OpenAIAdminClient:
    """Client for OpenAI Admin API"""
    
    def __init__(self, admin_key: Optional[str] = None):
        self.admin_key = admin_key or os.getenv("OPENAI_ADMIN_KEY")
        if not self.admin_key:
            raise ValueError("OPENAI_ADMIN_KEY environment variable or --admin-key argument required")
        
        self.base_url = "https://api.openai.com/v1/organization"
        self.headers = {
            "Authorization": f"Bearer {self.admin_key}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, params: Optional[dict] = None, json: Optional[dict] = None):
        """Make API request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        
        # Log the request
        logger.info(f"API Request: {method} {url}")
        logger.debug(f"Request params: {params}")
        logger.debug(f"Request body: {json}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=json
            )
            
            # Log the response
            logger.info(f"API Response: {response.status_code} for {method} {url}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            logger.debug(f"Response body: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Log the error details
            logger.error(f"HTTP Error: {e}")
            logger.error(f"Status Code: {e.response.status_code if e.response else 'N/A'}")
            logger.error(f"Response body: {e.response.text if e.response else 'N/A'}")
            try:
                error_json = e.response.json() if e.response else {}
                logger.error(f"Error JSON: {error_json}")
            except:
                pass
            # Re-raise HTTP errors so callers can handle them
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in API request: {e}")
            click.echo(f"Unexpected error: {e}", err=True)
            sys.exit(1)
    
    def list_users(self, limit: int = 100) -> dict:
        """List all users in the organization"""
        return self._request("GET", "users", params={"limit": limit})
    
    def list_projects(self, include_archived: bool = False, limit: int = 100) -> dict:
        """List all projects in the organization"""
        return self._request("GET", "projects", params={
            "include_archived": include_archived,
            "limit": limit
        })
    
    def list_admin_keys(self, limit: int = 100) -> dict:
        """List all admin API keys"""
        return self._request("GET", "admin_api_keys", params={"limit": limit})
    
    def list_project_api_keys(self, project_id: str, limit: int = 100) -> dict:
        """List API keys for a specific project"""
        return self._request("GET", f"projects/{project_id}/api_keys", params={"limit": limit})
    
    def get_project_api_key(self, project_id: str, key_id: str) -> dict:
        """Get a specific API key from a project"""
        return self._request("GET", f"projects/{project_id}/api_keys/{key_id}")
    
    def get_usage_completions(self, start_time: int, end_time: Optional[int] = None, 
                             group_by: Optional[List[str]] = None, limit: int = 7,
                             project_ids: Optional[List[str]] = None, 
                             models: Optional[List[str]] = None) -> dict:
        """Get completions usage data"""
        params = {
            "start_time": start_time,
            "limit": limit
        }
        if end_time:
            params["end_time"] = end_time
        if group_by:
            params["group_by"] = group_by
        if project_ids:
            params["project_ids"] = project_ids
        if models:
            params["models"] = models
        return self._request("GET", "usage/completions", params=params)
    
    def get_usage_embeddings(self, start_time: int, end_time: Optional[int] = None,
                            group_by: Optional[List[str]] = None, limit: int = 7) -> dict:
        """Get embeddings usage data"""
        params = {"start_time": start_time, "limit": limit}
        if end_time:
            params["end_time"] = end_time
        if group_by:
            params["group_by"] = group_by
        return self._request("GET", "usage/embeddings", params=params)
    
    def get_usage_images(self, start_time: int, end_time: Optional[int] = None,
                        group_by: Optional[List[str]] = None, limit: int = 7) -> dict:
        """Get images usage data"""
        params = {"start_time": start_time, "limit": limit}
        if end_time:
            params["end_time"] = end_time
        if group_by:
            params["group_by"] = group_by
        return self._request("GET", "usage/images", params=params)
    
    def get_usage_audio_speeches(self, start_time: int, end_time: Optional[int] = None,
                                 group_by: Optional[List[str]] = None, limit: int = 7) -> dict:
        """Get audio speeches (TTS) usage data"""
        params = {"start_time": start_time, "limit": limit}
        if end_time:
            params["end_time"] = end_time
        if group_by:
            params["group_by"] = group_by
        return self._request("GET", "usage/audio_speeches", params=params)
    
    def get_usage_audio_transcriptions(self, start_time: int, end_time: Optional[int] = None,
                                       group_by: Optional[List[str]] = None, limit: int = 7) -> dict:
        """Get audio transcriptions (Whisper) usage data"""
        params = {"start_time": start_time, "limit": limit}
        if end_time:
            params["end_time"] = end_time
        if group_by:
            params["group_by"] = group_by
        return self._request("GET", "usage/audio_transcriptions", params=params)
    
    def get_costs(self, start_time: int, end_time: Optional[int] = None,
                  group_by: Optional[List[str]] = None, limit: int = 7,
                  project_ids: Optional[List[str]] = None) -> dict:
        """Get costs data"""
        params = {"start_time": start_time, "limit": limit}
        if end_time:
            params["end_time"] = end_time
        if group_by:
            params["group_by"] = group_by
        if project_ids:
            params["project_ids"] = project_ids
        return self._request("GET", "costs", params=params)
    
    def list_audit_logs(self, after: Optional[str] = None, before: Optional[str] = None,
                       limit: int = 20, effective_at_gt: Optional[int] = None,
                       effective_at_gte: Optional[int] = None, effective_at_lt: Optional[int] = None,
                       effective_at_lte: Optional[int] = None, project_ids: Optional[List[str]] = None,
                       event_types: Optional[List[str]] = None, actor_ids: Optional[List[str]] = None,
                       actor_emails: Optional[List[str]] = None, resource_ids: Optional[List[str]] = None) -> dict:
        """List audit logs with optional filters"""
        params = {"limit": limit}
        
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        
        # Effective date range - use bracket notation for nested params
        if effective_at_gt:
            params["effective_at[gt]"] = effective_at_gt
        if effective_at_gte:
            params["effective_at[gte]"] = effective_at_gte
        if effective_at_lt:
            params["effective_at[lt]"] = effective_at_lt
        if effective_at_lte:
            params["effective_at[lte]"] = effective_at_lte
        
        # Array filters
        if project_ids:
            params["project_ids[]"] = project_ids
        if event_types:
            params["event_types[]"] = event_types
        if actor_ids:
            params["actor_ids[]"] = actor_ids
        if actor_emails:
            params["actor_emails[]"] = actor_emails
        if resource_ids:
            params["resource_ids[]"] = resource_ids
        
        return self._request("GET", "audit_logs", params=params)
    
    def get_project(self, project_id: str) -> dict:
        """Get a specific project"""
        return self._request("GET", f"projects/{project_id}")
    
    def list_project_users(self, project_id: str, limit: int = 100) -> dict:
        """List users in a project"""
        return self._request("GET", f"projects/{project_id}/users", params={"limit": limit})
    
    def list_project_service_accounts(self, project_id: str, limit: int = 100) -> dict:
        """List service accounts in a project"""
        return self._request("GET", f"projects/{project_id}/service_accounts", params={"limit": limit})
    
    def get_project_service_account(self, project_id: str, service_account_id: str) -> dict:
        """Get a specific service account from a project"""
        return self._request("GET", f"projects/{project_id}/service_accounts/{service_account_id}")
    
    def list_project_rate_limits(self, project_id: str, limit: int = 100) -> dict:
        """List rate limits for a project"""
        return self._request("GET", f"projects/{project_id}/rate_limits", params={"limit": limit})
    
    def update_project_rate_limit(self, project_id: str, rate_limit_id: str, **kwargs) -> dict:
        """Update a rate limit for a project
        
        Supported kwargs:
        - max_requests_per_1_minute: int
        - max_tokens_per_1_minute: int
        - max_images_per_1_minute: int
        - max_audio_megabytes_per_1_minute: int
        - max_requests_per_1_day: int
        - batch_1_day_max_input_tokens: int
        """
        # Filter out None values
        data = {k: v for k, v in kwargs.items() if v is not None}
        return self._request("POST", f"projects/{project_id}/rate_limits/{rate_limit_id}", json=data)
    
    def create_project(self, name: str) -> dict:
        """Create a new project"""
        return self._request("POST", "projects", json={"name": name})
    
    def add_project_user(self, project_id: str, user_id: str, role: str) -> dict:
        """Add a user to a project"""
        return self._request("POST", f"projects/{project_id}/users", json={"user_id": user_id, "role": role})
    
    def create_project_service_account(self, project_id: str, name: str) -> dict:
        """Create a service account in a project"""
        return self._request("POST", f"projects/{project_id}/service_accounts", json={"name": name})
    
    def archive_project(self, project_id: str) -> dict:
        """Archive a project"""
        return self._request("POST", f"projects/{project_id}/archive")
    
    def delete_project_api_key(self, project_id: str, key_id: str) -> dict:
        """Delete an API key from a project"""
        return self._request("DELETE", f"projects/{project_id}/api_keys/{key_id}")
    
    def delete_project_user(self, project_id: str, user_id: str) -> dict:
        """Delete a user from a project"""
        return self._request("DELETE", f"projects/{project_id}/users/{user_id}")
    
    def delete_project_service_account(self, project_id: str, service_account_id: str) -> dict:
        """Delete a service account from a project"""
        return self._request("DELETE", f"projects/{project_id}/service_accounts/{service_account_id}")
