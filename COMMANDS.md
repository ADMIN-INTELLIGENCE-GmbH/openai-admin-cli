# OpenAI Admin CLI - Command Reference

## Users
- `users list` - List all organization users

## Projects
- `projects list` - List all projects
- `projects export-template PROJECT_ID` - Export project config (users, service accounts, rate limits)
- `projects create-from-template FILE` - Create project from template
- `projects delete PROJECT_ID` - Archive project(s)

## API Keys
- `keys list-admin` - List admin API keys
- `keys list-project PROJECT_ID` - List project API keys
- `keys get PROJECT_ID KEY_ID` - Get details of a specific API key
- `keys delete PROJECT_ID KEY_ID` - Delete an API key from a project (user keys only)

## Service Accounts
- `service-accounts list PROJECT_ID` - List all service accounts in a project
- `service-accounts create PROJECT_ID NAME` - Create a new service account (generates API key)
- `service-accounts get PROJECT_ID SERVICE_ACCOUNT_ID` - Get service account details
- `service-accounts delete PROJECT_ID SERVICE_ACCOUNT_ID` - Delete service account and its keys

## Rate Limits
- `rate-limits list PROJECT_ID` - List all rate limits for a project
- `rate-limits update PROJECT_ID RATE_LIMIT_ID` - Update rate limit settings for a model

## Usage Analytics
- `usage completions` - Chat/text completion usage
- `usage embeddings` - Embeddings usage
- `usage images` - Image generation usage
- `usage audio-speeches` - TTS usage
- `usage audio-transcriptions` - Whisper usage

## Costs
- `costs` - Organization spending breakdown

## Notes
- User API keys cannot be created via API (OpenAI limitation)
- Service accounts can be created programmatically
- Creating a service account automatically generates an API key
- Service account API keys are shown only once during creation
- Deleting a service account deletes all its API keys
- Rate limits can be set per-model and per-project for cost/performance control
- Rate limits cannot exceed organization-level limits
