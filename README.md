# OpenAI Admin CLI

A powerful command-line tool for managing your OpenAI organization using the Admin API.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [List Users](#list-users)
  - [List Projects](#list-projects)
  - [List API Keys](#list-api-keys)
    - [List Admin Keys](#list-admin-keys)
    - [List Project Keys](#list-project-keys)
    - [Get API Key Details](#get-api-key-details)
    - [Delete API Key](#delete-api-key)
  - [Service Account Management](#service-account-management)
    - [List Service Accounts](#list-service-accounts)
    - [Create Service Account](#create-service-account)
    - [Get Service Account Details](#get-service-account-details)
    - [Delete Service Account](#delete-service-account)
  - [Rate Limits Management](#rate-limits-management)
    - [List Rate Limits](#list-rate-limits)
    - [Update Rate Limits](#update-rate-limits)
  - [Usage Analytics](#usage-analytics)
    - [Completions Usage](#completions-usage)
    - [Embeddings Usage](#embeddings-usage)
    - [Image Generation Usage](#image-generation-usage)
    - [Audio Speeches Usage (TTS)](#audio-speeches-usage-tts)
    - [Audio Transcriptions Usage (Whisper)](#audio-transcriptions-usage-whisper)
  - [Cost Tracking](#cost-tracking)
  - [Notifications](#notifications)
    - [Quick Start](#quick-start)
    - [Notification Commands](#notification-commands)
    - [Use Cases](#use-cases)
    - [Message Format](#message-format)
- [Environment Variables](#environment-variables)
  - [Setting up Notifications](#setting-up-notifications)
- [Output Formats](#output-formats)
  - [Table Format (Default)](#table-format-default)
  - [JSON Format](#json-format)
- [Common Use Cases](#common-use-cases)
- [Example Scripts (NEW in v1.2.0)](#example-scripts)
  - [Monitoring Scripts](#monitoring-scripts-1)
  - [Security Scripts](#security-scripts-1)
- [Security Notes](#security-notes)
- [Troubleshooting](#troubleshooting)
- [Future Features](#future-features)
- [Changelog](#changelog)
- [Contributing](#contributing)
- [Author](#author)
- [License](#license)

## Features

- **Notification System**: Send command results to users via Mattermost for remote execution and monitoring
- **List Users**: View all users in your organization with their roles and details
- **List Projects**: See all projects (active and archived) in your organization
- **Project Templates**: Export and import project configurations (users, service accounts, rate limits)
- **Service Account Management**: 
  - Create, list, view, and delete service accounts
  - Automatic API key generation when creating service accounts
- **API Key Management**: 
  - View all admin API keys
  - View project-specific API keys (user and service account keys)
  - Get detailed information about specific keys
  - Delete user API keys (service account keys deleted via service account deletion)
- **Rate Limits Management**:
  - View rate limits for all models in a project
  - Get detailed rate limit information for specific models
  - Update rate limits to control costs and prevent abuse
  - Set per-minute and per-day limits for requests, tokens, images, and audio
- **Usage Analytics**: Track detailed usage metrics for:
  - Completions (chat/text models)
  - Embeddings
  - Image generation
  - Audio speeches (TTS)
  - Audio transcriptions (Whisper)
- **Cost Tracking**: Monitor spending across projects and line items
- **Audit Logs**: Security and compliance monitoring with detailed event tracking

## Installation

1. Clone this repository or download the files

2. Install dependencies:
```bash
python3 -m pip install -r requirements.txt
```

3. Set up your Admin API key:
```bash
export OPENAI_ADMIN_KEY="your-admin-api-key-here"
```

To get an Admin API Key, visit: https://platform.openai.com/settings/organization/admin-keys

## Usage

Make the script executable (optional):
```bash
chmod +x openai_admin.py
```

### List Users

```bash
python openai_admin.py users list
```

Options:
- `--limit N` - Limit number of results (default: 100)
- `--format [table|json]` - Output format (default: table)

Example:
```bash
# List all users in table format
python openai_admin.py users list

# Get JSON output
python openai_admin.py users list --format json
```

### List Projects

```bash
python openai_admin.py projects list
```

Options:
- `--include-archived` - Include archived projects
- `--limit N` - Limit number of results (default: 100)
- `--format [table|json]` - Output format (default: table)

Examples:
```bash
# List active projects
python openai_admin.py projects list

# List all projects including archived
python openai_admin.py projects list --include-archived

# Get JSON output
python openai_admin.py projects list --format json
```

### List API Keys

#### List Admin Keys

```bash
python openai_admin.py keys list-admin
```

Options:
- `--limit N` - Limit number of results (default: 100)
- `--format [table|json]` - Output format (default: table)

Example:
```bash
python openai_admin.py keys list-admin
```

#### List Project Keys

```bash
python openai_admin.py keys list-project PROJECT_ID
```

Options:
- `--limit N` - Limit number of results (default: 100)
- `--format [table|json]` - Output format (default: table)

Example:
```bash
# First, get your project ID
python openai_admin.py projects list

# Then list keys for that project
python openai_admin.py keys list-project proj_abc123
```

#### Get API Key Details

Get detailed information about a specific API key:

```bash
python openai_admin.py keys get PROJECT_ID KEY_ID
```

Options:
- `--format [table|json]` - Output format (default: table)

Example:
```bash
# Get details of a specific key
python openai_admin.py keys get proj_abc123 key_xyz789

# JSON output for scripting
python openai_admin.py keys get proj_abc123 key_xyz789 --format json
```

This shows:
- Key ID, name, and redacted value
- Creation date and last usage date
- Owner information (user details or service account info)

#### Delete API Key

Delete a user's API key from a project:

```bash
python openai_admin.py keys delete PROJECT_ID KEY_ID
```

Options:
- `--force` - Skip confirmation prompt

Example:
```bash
# Delete with confirmation prompt
python openai_admin.py keys delete proj_abc123 key_xyz789

# Force delete without confirmation
python openai_admin.py keys delete proj_abc123 key_xyz789 --force
```

**Important Notes:**
- Can only delete **user API keys** via this command
- **Service account API keys** cannot be deleted individually
- To remove a service account's key, delete the entire service account using `service-accounts delete`

### Service Account Management

Service accounts are bot users not tied to individual people. When a human user leaves your organization, their keys stop working. Service accounts persist and are ideal for production deployments, CI/CD pipelines, and automated systems.

#### List Service Accounts

```bash
python openai_admin.py service-accounts list PROJECT_ID
```

Options:
- `--limit N` - Limit number of results (default: 100)
- `--format [table|json]` - Output format (default: table)

Example:
```bash
# List service accounts in a project
python openai_admin.py service-accounts list proj_abc123

# JSON output
python openai_admin.py service-accounts list proj_abc123 --format json
```

#### Create Service Account

Create a new service account with an automatically generated API key:

```bash
python openai_admin.py service-accounts create PROJECT_ID NAME
```

Example:
```bash
# Create a service account for production
python openai_admin.py service-accounts create proj_abc123 "Production Bot"

# Create for CI/CD
python openai_admin.py service-accounts create proj_abc123 "GitHub Actions"
```

**Critical Information:**
- Creating a service account **automatically generates an API key**
- The API key value is **displayed only once** during creation
- **Save the API key immediately** - it cannot be retrieved later
- If you lose the key, you must delete the service account and create a new one

Example Output:
```
================================================================================
[SUCCESS] Service Account Created Successfully!
================================================================================
ID:         svc_acct_abc123
Name:       Production Bot
Role:       member
Created At: 2024-03-26 10:25:33

================================================================================
[WARNING] API KEY (SAVE THIS NOW - IT WON'T BE SHOWN AGAIN!)
================================================================================
Key ID:     key_xyz789
Key Name:   Secret Key
Key Value:  sk-proj-abcdefghijklmnop...
Created At: 2024-03-26 10:25:33
================================================================================

[WARNING] This API key value is displayed only once!
   Save it in a secure location immediately.
```

#### Get Service Account Details

Retrieve information about a specific service account:

```bash
python openai_admin.py service-accounts get PROJECT_ID SERVICE_ACCOUNT_ID
```

Options:
- `--format [table|json]` - Output format (default: table)

Example:
```bash
python openai_admin.py service-accounts get proj_abc123 svc_acct_xyz
```

#### Delete Service Account

Delete a service account and all its API keys:

```bash
python openai_admin.py service-accounts delete PROJECT_ID SERVICE_ACCOUNT_ID
```

Options:
- `--force` - Skip confirmation prompt

Example:
```bash
# Delete with confirmation
python openai_admin.py service-accounts delete proj_abc123 svc_acct_xyz

# Force delete without prompt
python openai_admin.py service-accounts delete proj_abc123 svc_acct_xyz --force
```

**Warning:**
- Deleting a service account **also deletes all its API keys**
- This action **cannot be undone**
- Any systems using those API keys will immediately lose access

### Rate Limits Management

Rate limits control API usage per model and per project. This is crucial for **cost control**, **preventing abuse**, and **managing performance**. You can set limits lower than your organization's limits but cannot exceed them.

#### List Rate Limits

View all rate limits configured for a project:

```bash
python openai_admin.py rate-limits list PROJECT_ID
```

Options:
- `--limit N` - Maximum number of rate limits to return (default: 100)
- `--format [table|json]` - Output format (default: table)

Example:
```bash
# List all rate limits for a project
python openai_admin.py rate-limits list proj_abc123

# JSON output for scripting
python openai_admin.py rate-limits list proj_abc123 --format json
```

The output shows:
- Model name (e.g., `gpt-4`, `gpt-3.5-turbo`, `dall-e-3`)
- Maximum requests per minute
- Maximum tokens per minute
- Maximum images per minute (for image models)
- Maximum audio MB per minute (for audio models)
- Maximum requests per day
- Maximum batch tokens per day

**Note:** The OpenAI Admin API does not support retrieving individual rate limit details. Use the `list` command to view all rate limits for a project.

#### Update Rate Limits

Modify rate limits for a model to control costs and usage:

```bash
python openai_admin.py rate-limits update PROJECT_ID RATE_LIMIT_ID [OPTIONS]
```

Options (specify only the limits you want to change):
- `--max-requests-per-minute INT` - Maximum requests per minute
- `--max-tokens-per-minute INT` - Maximum tokens per minute
- `--max-images-per-minute INT` - Maximum images per minute (image models)
- `--max-audio-mb-per-minute INT` - Maximum audio MB per minute (audio models)
- `--max-requests-per-day INT` - Maximum requests per day
- `--batch-max-tokens-per-day INT` - Maximum batch input tokens per day

Examples:

```bash
# Reduce GPT-4 usage to control costs
python openai_admin.py rate-limits update proj_abc123 rl_gpt4 \
  --max-requests-per-minute 50 \
  --max-tokens-per-minute 10000

# Set daily limit for DALL-E
python openai_admin.py rate-limits update proj_abc123 rl_dalle3 \
  --max-images-per-minute 5 \
  --max-requests-per-day 100

# Increase limits for production project
python openai_admin.py rate-limits update proj_prod rl_gpt35turbo \
  --max-requests-per-minute 5000 \
  --max-tokens-per-minute 1000000
```

**Important Notes:**
- **Cannot exceed organization limits** - Project limits must be ≤ organization limits
- **Use for cost control** - Set conservative limits for dev/test projects
- **Performance tuning** - Adjust limits based on actual usage patterns
- **Monitor usage** - Use `usage` commands to see actual consumption vs limits

**Common Use Cases:**

1. **Development Environment** - Low limits to prevent accidental overspending:
   ```bash
   python openai_admin.py rate-limits update proj_dev rl_gpt4 \
     --max-requests-per-minute 10 \
     --max-tokens-per-minute 5000
   ```

2. **Production Environment** - Higher limits for business-critical apps:
   ```bash
   python openai_admin.py rate-limits update proj_prod rl_gpt4 \
     --max-requests-per-minute 1000 \
     --max-tokens-per-minute 500000
   ```

3. **Cost Cap** - Set daily limits to prevent monthly bill surprises:
   ```bash
   python openai_admin.py rate-limits update proj_abc123 rl_gpt4 \
     --max-requests-per-day 10000
   ```

### Usage Analytics

#### Completions Usage

Track usage for chat and text completion models:

```bash
# Quick usage - last 7 days
python openai_admin.py usage completions --days 7

# Or specify exact date range
python openai_admin.py usage completions --start-date 2024-01-01
```

Options:
- `--start-date YYYY-MM-DD` - Start date (either this or --days required)
- `--end-date YYYY-MM-DD` - End date (defaults to now)
- `--days N` - Alternative to --start-date: look back N days from now
- `--group-by FIELD` - Group by: project_id, user_id, api_key_id, model, batch, service_tier (can be used multiple times)
- `--project-id ID` - Filter by project ID (can be used multiple times)
- `--model NAME` - Filter by model name (can be used multiple times)
- `--limit N` - Number of time buckets to return (default: 7)
- `--format [table|json]` - Output format (default: table)

Examples:
```bash
# Quick look at last 7 days
python openai_admin.py usage completions --days 7

# Last 30 days
python openai_admin.py usage completions --days 30

# Specific date range
python openai_admin.py usage completions --start-date 2024-01-01 --end-date 2024-01-31

# Group by project and model
python openai_admin.py usage completions --days 30 --group-by project_id --group-by model

# Filter specific projects and models
python openai_admin.py usage completions --days 30 --project-id proj_123 --model gpt-4
```

#### Embeddings Usage

Track embeddings API usage:

```bash
# Quick usage - last 7 days
python openai_admin.py usage embeddings --days 7

# Or specify exact date range
python openai_admin.py usage embeddings --start-date 2024-01-01
```

Options:
- `--start-date YYYY-MM-DD` - Start date (either this or --days required)
- `--end-date YYYY-MM-DD` - End date (defaults to now)
- `--days N` - Alternative to --start-date: look back N days from now
- `--group-by FIELD` - Group by: project_id, user_id, api_key_id, model
- `--limit N` - Number of time buckets to return (default: 7)
- `--format [table|json]` - Output format (default: table)

#### Image Generation Usage

Track DALL-E and image generation usage:

```bash
# Quick usage - last 7 days
python openai_admin.py usage images --days 7

# Or specify exact date range
python openai_admin.py usage images --start-date 2024-01-01
```

Options:
- `--start-date YYYY-MM-DD` - Start date (either this or --days required)
- `--end-date YYYY-MM-DD` - End date (defaults to now)
- `--days N` - Alternative to --start-date: look back N days from now
- `--group-by FIELD` - Group by: project_id, model, size, source
- `--limit N` - Number of time buckets to return (default: 7)
- `--format [table|json]` - Output format (default: table)

#### Audio Speeches Usage (TTS)

Track text-to-speech usage:

```bash
# Quick usage - last 7 days
python openai_admin.py usage audio-speeches --days 7

# Or specify exact date range
python openai_admin.py usage audio-speeches --start-date 2024-01-01
```

Options:
- `--start-date YYYY-MM-DD` - Start date (either this or --days required)
- `--days N` - Alternative to --start-date: look back N days from now
- `--group-by FIELD` - Group by: project_id, model
- `--format [table|json]` - Output format (default: table)

#### Audio Transcriptions Usage (Whisper)

Track Whisper transcription usage:

```bash
# Quick usage - last 7 days
python openai_admin.py usage audio-transcriptions --days 7

# Or specify exact date range
python openai_admin.py usage audio-transcriptions --start-date 2024-01-01
```

Options:
- `--start-date YYYY-MM-DD` - Start date (either this or --days required)
- `--days N` - Alternative to --start-date: look back N days from now
- `--group-by FIELD` - Group by: project_id, model
- `--format [table|json]` - Output format (default: table)

### Cost Tracking

Monitor your organization's spending:

```bash
# Quick look at last 30 days
python openai_admin.py costs --days 30

# Or specify exact date range
python openai_admin.py costs --start-date 2024-01-01
```

Options:
- `--start-date YYYY-MM-DD` - Start date (either this or --days required)
- `--end-date YYYY-MM-DD` - End date (defaults to now)
- `--days N` - Alternative to --start-date: look back N days from now
- `--group-by FIELD` - Group by: project_id, line_item (can be used multiple times)
- `--project-id ID` - Filter by project ID (can be used multiple times)
- `--limit N` - Number of time buckets to return (default: 7)
- `--format [table|json]` - Output format (default: table)

Examples:
```bash
# Last 30 days of costs
python openai_admin.py costs --days 30

# Last 7 days
python openai_admin.py costs --days 7

# Specific date range
python openai_admin.py costs --start-date 2024-01-01 --end-date 2024-01-31

# Group by project to see per-project spending
python openai_admin.py costs --days 30 --group-by project_id

# Group by line item to see detailed breakdown
python openai_admin.py costs --days 7 --group-by line_item

# Specific project costs
python openai_admin.py costs --days 30 --project-id proj_123
```

## Notifications

Send command results to users via Mattermost for remote monitoring and async execution. Perfect for long-running operations, scheduled tasks, or notifying team members of changes.

### Quick Start

```bash
# Send command output to user ID 49 via Mattermost
python openai_admin.py projects list --notify 49 --channel mattermost

# Works with any command - at the end
python openai_admin.py users list --limit 10 --notify 49 --channel mattermost

# Or at the beginning
python openai_admin.py --notify 49 --channel mattermost projects list --limit 10
```

### Notification Commands

#### Test Notifications

```bash
# Send a test message
python openai_admin.py notify test 49

# Custom test message
python openai_admin.py notify test 49 --message "Testing the notification system"
```

#### List Available Users

```bash
# See all configured users for notifications
python openai_admin.py notify list-users
```

Output:
```
[INFO] Available users for mattermost notifications:

  User ID: 49
    Name:  Julian Billinger
    Email: julian.billinger@admin-intelligence.com
    MM User ID: pdmno8z8yib9ij8grd4ut8i6ye
    MM Channel ID: smz4idhmsf8y5y7nc1yg8ibnbe

Total: 1 users configured
```

#### Check System Status

```bash
# Verify notification system configuration
python openai_admin.py notify status
```

### Use Cases

**Remote Execution:**
```bash
# Run on a server, get results in Mattermost
python openai_admin.py projects delete proj_old123 --force --notify 49 --channel mattermost
```

**Long-Running Operations:**
```bash
# Get notified when large data exports complete
python openai_admin.py usage completions --days 365 --notify 49 --channel mattermost
```

**Team Notifications:**
```bash
# Notify team lead when service account is created
python openai_admin.py service-accounts create proj_prod "API Bot" --notify 49 --channel mattermost
```

**Audit Trail:**
```bash
# Send audit logs to compliance team
python openai_admin.py audit list --days 7 --notify 49 --channel mattermost
```

### Message Format

Messages are formatted with:
- ✅ Success indicator (or ❌ for failures)
- Command that was executed
- Full command output
- Timestamp

Example notification:
```
✅ OpenAI Admin CLI - Success

Command: openai_admin.py projects list

Output:
Fetching projects...

Total projects: 5

+-------------------------------+-----------------+----------+
| ID                            | Name            | Status   |
+===============================+=================+==========+
| proj_R1hXkN2ReRX94yfyT0gewFz4 | Default project | active   |
+-------------------------------+-----------------+----------+
...
```

For more details, see [NOTIFICATIONS.md](NOTIFICATIONS.md).

## Output Formats
```

## Environment Variables

- `OPENAI_ADMIN_KEY` - Your OpenAI Admin API key (required)
- `MATTERMOST_BOT_TOKEN` - Mattermost bot token for notifications (optional)
- `MATTERMOST_BOT_ID` - Mattermost bot ID for notifications (optional)
- `MATTERMOST_BASE_URL` - Mattermost API base URL (optional, defaults to https://chat.admin-intelligence.de/api/v4)

You can also pass the admin key as a command-line option:
```bash
python openai_admin.py --admin-key sk-admin-... users list
```

### Setting up Notifications

To enable Mattermost notifications, add these to your `.env` file:

```env
OPENAI_ADMIN_KEY="sk-admin-..."
MATTERMOST_BOT_TOKEN="your_bot_token"
MATTERMOST_BOT_ID="your_bot_id"
MATTERMOST_BASE_URL="https://chat.admin-intelligence.de/api/v4"
```

To enable Email notifications, add these to your `.env` file:

```env
MAIL_HOST=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_password
MAIL_FROM_ADDRESS=noreply@example.com
MAIL_FROM_NAME="OpenAI Admin CLI"
```

Then configure user mappings in `config/users.json`:

```json
{
  "users": {
    "49": {
      "name": "Julian Billinger",
      "email": "julian.billinger@admin-intelligence.com",
      "mattermost_user_id": "pdmno8z8yib9ij8grd4ut8i6ye",
      "mattermost_channel_id": "smz4idhmsf8y5y7nc1yg8ibnbe"
    }
  }
}
```

**Note:** For email notifications, only the `name` and `email` fields are required. The Mattermost fields are optional and only needed if you want to use Mattermost notifications.

## Output Formats

### Table Format (Default)
Clean, readable tables in your terminal:
```
Total users: 3

+-------------+-----------+--------------------+--------+---------------------+
| ID          | Name      | Email              | Role   | Added At            |
+=============+===========+====================+========+=====================+
| user_abc    | John Doe  | john@example.com   | owner  | 2024-03-26 10:25:33 |
+-------------+-----------+--------------------+--------+---------------------+
```

### JSON Format
Raw API response for scripting and automation:
```bash
python openai_admin.py users list --format json | jq '.data[] | {name, email, role}'
```

## Common Use Cases

### Audit organization access
```bash
# See all users and their roles
python openai_admin.py users list

# Check who has access to a specific project
python openai_admin.py keys list-project proj_123

# List all service accounts in a project
python openai_admin.py service-accounts list proj_123
```

### Set up service accounts for production
```bash
# Create a service account for your production application
python openai_admin.py service-accounts create proj_123 "Production API Bot"

# IMPORTANT: Copy and save the API key shown - it won't be displayed again!
# Store it securely (e.g., in your environment variables or secrets manager)

# List all service accounts to verify
python openai_admin.py service-accounts list proj_123
```

### Manage API keys
```bash
# View details of a specific API key
python openai_admin.py keys get proj_123 key_xyz

# Delete a compromised user API key
python openai_admin.py keys delete proj_123 key_xyz

# Delete a service account (and all its keys)
python openai_admin.py service-accounts delete proj_123 svc_acct_abc
```

### Monitor API key usage
```bash
# See when admin keys were last used
python openai_admin.py keys list-admin

# Check project-specific key usage
python openai_admin.py keys list-project proj_123

# Get detailed info about a specific key
python openai_admin.py keys get proj_123 key_xyz
```

### Review project structure
```bash
# See all active projects
python openai_admin.py projects list

# Include archived projects for cleanup
python openai_admin.py projects list --include-archived
```

### Analyze usage patterns
```bash
# See which models are being used most
python openai_admin.py usage completions --days 30 --group-by model

# Check usage by project
python openai_admin.py usage completions --days 7 --group-by project_id

# Track token usage over time
python openai_admin.py usage completions --start-date 2024-01-01 --end-date 2024-01-31
```

### Monitor costs and spending
```bash
# Total costs for the last month
python openai_admin.py costs --days 30

# Per-project cost breakdown
python openai_admin.py costs --days 30 --group-by project_id

# Detailed line-item costs
python openai_admin.py costs --start-date 2024-01-01 --group-by project_id --group-by line_item
```

## Example Scripts

**NEW in Version 1.2.0!** Pre-built automation scripts for monitoring and security workflows.

The `examples/` directory contains ready-to-use shell scripts for common operational tasks:

### Monitoring Scripts

Located in `examples/monitoring/`:

- **`daily-usage-report.sh`** - Daily usage summary across all API types (completions, embeddings, images, audio)
- **`weekly-cost-report.sh`** - Weekly cost breakdown by project and line item
- **`monthly-billing-summary.sh`** - Comprehensive end-of-month report with recommendations

**Quick Start:**
```bash
# Run daily usage report
./examples/monitoring/daily-usage-report.sh

# Get last 7 days with notification
./examples/monitoring/daily-usage-report.sh --days 7 --notify 49 --channel mattermost

# Weekly costs sent via email
./examples/monitoring/weekly-cost-report.sh --notify 49 --channel email
```

### Security Scripts

Located in `examples/security/`:

- **`audit-security-scan.sh`** - Scan audit logs for suspicious activities (key deletions, user changes, etc.)
- **`list-all-keys.sh`** - Complete inventory of all API keys across the organization
- **`unused-keys-report.sh`** - Identify keys not used in N days (default: 30)
- **`compliance-snapshot.sh`** - Generate comprehensive compliance report (users, projects, keys, service accounts, audit logs)

**Quick Start:**
```bash
# Run security audit
./examples/security/audit-security-scan.sh

# Find keys unused for 60+ days
./examples/security/unused-keys-report.sh --days 60

# Generate compliance snapshot
./examples/security/compliance-snapshot.sh
```

**Features:**
- ✅ All scripts support `--notify` and `--channel` for automated alerting
- ✅ JSON output (`--format json`) for integration with other tools
- ✅ Comprehensive help text (`--help`)
- ✅ Perfect for cron scheduling and CI/CD pipelines

**Learn More:**
See the complete documentation in [`examples/README.md`](examples/README.md) including:
- Detailed usage instructions
- Cron scheduling examples
- CI/CD integration patterns
- Best practices for automation

## Security Notes

- **Admin API keys have elevated privileges** - handle them securely
- Never commit your admin key to version control
- Consider using key rotation practices
- Admin keys can only be created by Organization Owners

## Troubleshooting

### "OPENAI_ADMIN_KEY environment variable required"
Set your admin API key:
```bash
export OPENAI_ADMIN_KEY="sk-admin-..."
```

### Import errors
Make sure dependencies are installed:
```bash
python3 -m pip install -r requirements.txt
```

### API errors
- Verify your admin key is valid
- Ensure you have Organization Owner permissions
- Check that the key hasn't expired

## Future Features

Coming soon:
- User management (invite, modify, delete)
- Rate limit management via templates
- Export reports to CSV/Excel
- Cost alerts and budgeting with thresholds
- Additional notification channels (Slack, Discord, PagerDuty)
- Interactive web dashboard
- Automated key rotation workflows
- Project provisioning templates
- Budget forecasting based on usage trends

## Changelog

### Version 1.2.0 - November 11, 2025

**New Features - Example Scripts for Automation:**
- **Example Scripts Directory**: Added `examples/` with pre-built automation scripts for monitoring and security
  - **Monitoring Scripts** (`examples/monitoring/`):
    - `daily-usage-report.sh` - Daily usage summary across all API types
    - `weekly-cost-report.sh` - Weekly cost breakdown by project and line item
    - `monthly-billing-summary.sh` - Comprehensive end-of-month billing report
  - **Security Scripts** (`examples/security/`):
    - `audit-security-scan.sh` - Scan audit logs for suspicious activities
    - `list-all-keys.sh` - Complete API key inventory across organization
    - `unused-keys-report.sh` - Identify keys not used in N days
    - `compliance-snapshot.sh` - Generate comprehensive compliance reports
  - All scripts support notifications (`--notify`, `--channel`)
  - All scripts support JSON output for integration
  - All scripts include comprehensive help text and error handling

**Documentation:**
- Added detailed [`examples/README.md`](examples/README.md) with:
  - Complete usage instructions for all scripts
  - Cron scheduling examples for automation
  - CI/CD integration patterns (GitHub Actions, etc.)
  - Best practices for production deployment
  - Troubleshooting guides
- Updated main README with Examples section and quick start guide
- Added Table of Contents entry for Example Scripts

**Use Cases Enabled:**
- Automated daily/weekly/monthly reporting
- Scheduled security audits
- Compliance snapshot generation
- Cost monitoring and alerting
- Key lifecycle management
- Continuous security monitoring

**Technical Details:**
- Scripts tested on macOS and Linux (Bash/Zsh)
- Portable shell scripts with minimal dependencies
- Structured output with color-coded sections
- Comprehensive error handling and validation
- Support for output redirection and logging

### Version 1.1.0 - November 11, 2025

**New Features:**
- **Notification System**: Send command results to users via Mattermost or Email
  - Added `--notify` and `--channel` options to all commands
  - Supports notification options at both root level and command level
  - Automatic output capture and formatting for notifications
  - New `notify` command group with test, list-users, and status subcommands
  - Integration with user mappings via `config/users.json`
  - **Email Support**: Send notifications via SMTP (configurable via MAIL_* environment variables)
  - **Mattermost Support**: Send notifications via Mattermost bot integration
  - See [NOTIFICATIONS.md](NOTIFICATIONS.md) for complete documentation

**Improvements:**
- **ID Display**: Removed truncation across all commands - now showing full IDs for:
  - Project IDs
  - User IDs
  - API Key IDs
  - Service Account IDs
  - Rate Limit IDs
  - Audit Log IDs
  - All usage analytics IDs
- **Code Organization**: Created modular notification system with `openai_admin/notifier.py`
- **Utilities**: Added `notification_options` decorator and `with_notification` wrapper for easy command integration

**Configuration:**
- Added support for `MATTERMOST_BOT_TOKEN`, `MATTERMOST_BOT_ID`, and `MATTERMOST_BASE_URL` environment variables
- Added support for `MAIL_HOST`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM_ADDRESS`, and `MAIL_FROM_NAME` environment variables
- Renamed `config/mattermost.json` to `config/users.json` for unified user management across notification channels

**Documentation:**
- Added comprehensive notification documentation in README
- Created detailed [NOTIFICATIONS.md](NOTIFICATIONS.md) guide
- Updated environment variables section with notification settings

**Commands Enhanced with Notifications:**
- `users list`
- `projects list`, `projects delete`
- `keys list-admin`, `keys list-project`, `keys get`, `keys delete`
- `service-accounts list`, `service-accounts create`, `service-accounts get`, `service-accounts delete`
- `rate-limits list`, `rate-limits update`
- `usage completions`, `usage embeddings`, `usage images`, `usage audio-speeches`, `usage audio-transcriptions`
- `costs`
- `audit list`

### Version 1.0.0 - Initial Release

**Core Features:**
- User management (list users)
- Project management (list, export templates, create from templates, delete/archive)
- API key management (list admin keys, list project keys, get key details, delete keys)
- Service account management (list, create, get, delete)
- Rate limits management (list, update)
- Usage analytics (completions, embeddings, images, audio speeches, audio transcriptions)
- Cost tracking and monitoring
- Audit log viewing and filtering
- Support for table and JSON output formats
- Comprehensive error handling and logging

## Contributing

Feel free to submit issues and enhancement requests!

## Author

**Julian Billinger**  
ADMIN INTELLIGENCE

For bugs, feature requests, or questions:
- Open an issue on GitHub
- Email: julian.billinger@admin-intelligence.com

## License

MIT License - feel free to use and modify as needed.
