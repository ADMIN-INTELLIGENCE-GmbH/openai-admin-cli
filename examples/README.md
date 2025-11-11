# OpenAI Admin CLI - Example Scripts

Automation scripts for monitoring, security, and operational tasks using the OpenAI Admin CLI.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Monitoring Scripts](#monitoring-scripts)
  - [Daily Usage Report](#daily-usage-report)
  - [Weekly Cost Report](#weekly-cost-report)
  - [Monthly Billing Summary](#monthly-billing-summary)
- [Security Scripts](#security-scripts)
  - [Audit Security Scan](#audit-security-scan)
  - [List All Keys](#list-all-keys)
  - [Unused Keys Report](#unused-keys-report)
  - [Compliance Snapshot](#compliance-snapshot)
- [Automation Tips](#automation-tips)
- [Scheduling with Cron](#scheduling-with-cron)
- [Integration Examples](#integration-examples)

## Overview

These scripts provide ready-to-use automation for common OpenAI Admin CLI workflows:

- **Monitoring Scripts** - Track usage, costs, and billing
- **Security Scripts** - Audit access, find unused keys, generate compliance reports

All scripts support:
- ✅ **Notifications** - Send results via Mattermost or Email
- ✅ **JSON Output** - Machine-readable format for integration
- ✅ **Flexible Scheduling** - Run manually or via cron
- ✅ **Comprehensive Logging** - Detailed output for debugging

## Prerequisites

1. **OpenAI Admin CLI** installed and configured
2. **Python Dependencies** - Install via:
   ```bash
   python3 -m pip install -r requirements.txt
   ```
   Or if using a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   
   **Note:** Scripts automatically activate `.venv` if it exists in the project root.

3. **Admin API Key** - Set in one of two ways:
   - **Option A (Recommended):** Create a `.env` file in the project root:
     ```bash
     # In /path/to/openai-helper/.env
     OPENAI_ADMIN_KEY="sk-admin-..."
     ```
   - **Option B:** Export as environment variable:
     ```bash
     export OPENAI_ADMIN_KEY="sk-admin-..."
     ```
   
   All scripts automatically load `.env` if it exists, making Option A more convenient.

4. **(Optional) Notification System** configured for alerts
5. **Bash shell** (zsh, bash - tested on macOS and Linux)

## Quick Start

```bash
# Navigate to examples directory
cd examples

# Run daily usage report
./monitoring/daily-usage-report.sh

# Run security scan
./security/audit-security-scan.sh

# Get help for any script
./monitoring/daily-usage-report.sh --help
```

## Monitoring Scripts

### Daily Usage Report

**Purpose:** Generate comprehensive daily usage summary across all usage types

**Location:** `examples/monitoring/daily-usage-report.sh`

**Features:**
- Completions usage (chat & text models)
- Embeddings usage
- Image generation usage
- Audio speeches (TTS)
- Audio transcriptions (Whisper)
- Grouped by project for cost attribution

**Usage:**

```bash
# Today's usage
./daily-usage-report.sh

# Last 7 days
./daily-usage-report.sh --days 7

# Send to team via Mattermost
./daily-usage-report.sh --notify 49 --channel mattermost

# JSON output for integration
./daily-usage-report.sh --format json --days 7
```

**Options:**
- `--days N` - Number of days to report (default: 1)
- `--notify USER_ID` - Send results to user via notification
- `--channel CHANNEL` - Notification channel (mattermost, email)
- `--format FORMAT` - Output format: table or json (default: table)

**Use Cases:**
- Daily standup reports
- Usage monitoring dashboard
- Automated alerts for usage spikes
- Team visibility into API consumption

---

### Weekly Cost Report

**Purpose:** Generate detailed weekly cost breakdown by project and line item

**Location:** `examples/monitoring/weekly-cost-report.sh`

**Features:**
- Total costs overview
- Per-project cost breakdown
- Line-item detailed analysis
- Trend identification

**Usage:**

```bash
# Last 7 days (default)
./weekly-cost-report.sh

# Last 30 days
./weekly-cost-report.sh --days 30

# Specific project only
./weekly-cost-report.sh --project-id proj_abc123

# Send to finance team
./weekly-cost-report.sh --notify 49 --channel email --days 7
```

**Options:**
- `--days N` - Number of days to report (default: 7)
- `--notify USER_ID` - Send results to user via notification
- `--channel CHANNEL` - Notification channel (mattermost, email)
- `--format FORMAT` - Output format: table or json
- `--project-id ID` - Filter by specific project (repeatable)

**Use Cases:**
- Weekly finance reviews
- Budget tracking
- Cost optimization identification
- Chargeback to departments/teams

---

### Monthly Billing Summary

**Purpose:** Comprehensive end-of-month report before billing cycle

**Location:** `examples/monitoring/monthly-billing-summary.sh`

**Features:**
- Organization overview (users, projects)
- 30-day cost analysis by project and line item
- Usage summary by model and project
- Recent security events from audit logs
- Actionable recommendations

**Usage:**

```bash
# Last 30 days (default)
./monthly-billing-summary.sh

# Last 60 days for comparison
./monthly-billing-summary.sh --days 60

# Send to leadership team
./monthly-billing-summary.sh --notify 49 --channel email
```

**Options:**
- `--days N` - Number of days to report (default: 30)
- `--notify USER_ID` - Send results to user via notification
- `--channel CHANNEL` - Notification channel (mattermost, email)
- `--format FORMAT` - Output format: table or json

**Use Cases:**
- Monthly finance meetings
- Executive reporting
- Budget planning
- Quarterly reviews

---

## Security Scripts

### Audit Security Scan

**Purpose:** Scan audit logs for suspicious activities and security events

**Location:** `examples/security/audit-security-scan.sh`

**Features:**
- API key creation, deletion, updates
- Service account changes
- User permission modifications
- Project changes
- Comprehensive event timeline

**Usage:**

```bash
# Last 7 days (default)
./audit-security-scan.sh

# Last 30 days
./audit-security-scan.sh --days 30

# Send security alert
./audit-security-scan.sh --notify 49 --channel email

# High severity only (coming soon)
./audit-security-scan.sh --severity high
```

**Options:**
- `--days N` - Number of days to scan (default: 7)
- `--notify USER_ID` - Send results to user via notification
- `--channel CHANNEL` - Notification channel (mattermost, email)
- `--format FORMAT` - Output format: table or json
- `--severity LEVEL` - Filter by severity (planned feature)

**Use Cases:**
- Daily security monitoring
- Incident response
- Compliance audits
- Unauthorized access detection

---

### List All Keys

**Purpose:** Complete inventory of all API keys across the organization

**Location:** `examples/security/list-all-keys.sh`

**Features:**
- Admin API keys
- Project-specific keys for all projects
- Service accounts per project
- Comprehensive key metadata

**Usage:**

```bash
# Display all keys
./list-all-keys.sh

# Save to file for audit
./list-all-keys.sh --output key-inventory-$(date +%Y%m%d).json --format json

# Send to security team
./list-all-keys.sh --notify 49 --channel email
```

**Options:**
- `--notify USER_ID` - Send results to user via notification
- `--channel CHANNEL` - Notification channel (mattermost, email)
- `--format FORMAT` - Output format: table or json
- `--output FILE` - Save output to file

**Use Cases:**
- Quarterly key audits
- Access reviews
- Key rotation planning
- Onboarding/offboarding verification

---

### Unused Keys Report

**Purpose:** Identify API keys that haven't been used in specified number of days

**Location:** `examples/security/unused-keys-report.sh`

**Features:**
- Finds keys unused for N days (default: 30)
- Identifies never-used keys
- Calculates days since last use
- Actionable deletion recommendations

**Usage:**

```bash
# Keys not used in 30 days (default)
./unused-keys-report.sh

# Keys not used in 90 days
./unused-keys-report.sh --days 90

# Save findings for review
./unused-keys-report.sh --output unused-keys-$(date +%Y%m%d).txt

# Alert security team
./unused-keys-report.sh --notify 49 --channel email --days 60
```

**Options:**
- `--days N` - Keys unused for N days (default: 30)
- `--notify USER_ID` - Send results to user via notification
- `--channel CHANNEL` - Notification channel (mattermost, email)
- `--format FORMAT` - Output format: table or json
- `--output FILE` - Save findings to file

**Use Cases:**
- Monthly key hygiene
- Security posture improvement
- Reduce attack surface
- Key lifecycle management

---

### Compliance Snapshot

**Purpose:** Generate comprehensive compliance snapshot of entire organization

**Location:** `examples/security/compliance-snapshot.sh`

**Features:**
- Complete organization structure (users, projects)
- All API keys (admin + project-specific)
- All service accounts
- 30 days of audit logs (configurable)
- Summary report + JSON data files
- Manifest file for automation

**Usage:**

```bash
# Generate snapshot with defaults
./compliance-snapshot.sh

# Custom output directory
./compliance-snapshot.sh --output-dir /path/to/compliance-reports

# Include 90 days of audit logs
./compliance-snapshot.sh --audit-days 90

# Notify compliance team when complete
./compliance-snapshot.sh --notify 49 --channel email
```

**Options:**
- `--output-dir DIR` - Directory to save reports (default: ./compliance-YYYYMMDD-HHMMSS)
- `--notify USER_ID` - Send completion notification
- `--channel CHANNEL` - Notification channel (mattermost, email)
- `--audit-days N` - Days of audit logs (default: 30)

**Output Structure:**
```
compliance-snapshot-20250111-143022/
├── manifest.json              # Snapshot metadata
├── summary.txt                # Human-readable summary
├── users.json                 # Organization users
├── projects.json              # All projects
├── admin-keys.json            # Admin API keys
├── audit-logs.json            # Audit events
├── project-keys/              # Per-project keys
│   ├── proj_abc123.json
│   └── proj_xyz789.json
└── service-accounts/          # Per-project service accounts
    ├── proj_abc123.json
    └── proj_xyz789.json
```

**Use Cases:**
- SOC 2 audits
- ISO 27001 compliance
- Internal security reviews
- Quarterly compliance reporting
- Change detection (compare snapshots)

---

## Automation Tips

### 1. Environment Setup

**All scripts automatically load `.env` from the project root** if it exists. This is the recommended approach:

```bash
# Create .env in project root: /path/to/openai-helper/.env
OPENAI_ADMIN_KEY="sk-admin-..."

# Optional - for notifications
MATTERMOST_BOT_TOKEN="your_token"
MATTERMOST_BOT_ID="your_bot_id"
MATTERMOST_BASE_URL="https://chat.example.com/api/v4"

# Optional - for email notifications
MAIL_HOST="smtp.example.com"
MAIL_PORT="587"
MAIL_USERNAME="your_email@example.com"
MAIL_PASSWORD="your_password"
MAIL_FROM_ADDRESS="noreply@example.com"
MAIL_FROM_NAME="OpenAI Admin CLI"
```

**Alternatively, export variables** in your shell (less convenient for automation):

```bash
export OPENAI_ADMIN_KEY="sk-admin-..."
```

**Note:** Scripts look for `.env` at `../../.env` relative to their location (project root).

### 2. Logging and Output

Capture script output for auditing:

```bash
# Log to file with timestamp
./daily-usage-report.sh 2>&1 | tee "logs/usage-$(date +%Y%m%d).log"

# JSON output for parsing
./weekly-cost-report.sh --format json > costs-$(date +%Y%m%d).json
```

### 3. Error Handling

Scripts use `set -euo pipefail` for robust error handling. Wrap in additional logic:

```bash
#!/bin/bash
if ! ./audit-security-scan.sh --notify 49 --channel email; then
    echo "Security scan failed! Manual review required."
    # Send alert, page on-call, etc.
fi
```

### 4. Parallel Execution

Run independent reports in parallel:

```bash
#!/bin/bash
./daily-usage-report.sh &
./weekly-cost-report.sh &
./audit-security-scan.sh &
wait
echo "All reports complete!"
```

---

## Scheduling with Cron

### Daily Usage Report (Every morning at 8 AM)

```cron
0 8 * * * cd /path/to/openai-helper/examples && ./monitoring/daily-usage-report.sh --notify 49 --channel mattermost
```

### Weekly Cost Report (Every Monday at 9 AM)

```cron
0 9 * * 1 cd /path/to/openai-helper/examples && ./monitoring/weekly-cost-report.sh --notify 49 --channel email
```

### Monthly Billing Summary (1st of month at 10 AM)

```cron
0 10 1 * * cd /path/to/openai-helper/examples && ./monitoring/monthly-billing-summary.sh --notify 49 --channel email
```

### Security Audit Scan (Daily at 2 AM)

```cron
0 2 * * * cd /path/to/openai-helper/examples && ./security/audit-security-scan.sh --notify 49 --channel email
```

### Unused Keys Report (Weekly on Sunday at 11 PM)

```cron
0 23 * * 0 cd /path/to/openai-helper/examples && ./security/unused-keys-report.sh --days 60 --notify 49 --channel email
```

### Compliance Snapshot (Monthly on 1st at midnight)

```cron
0 0 1 * * cd /path/to/openai-helper/examples && ./security/compliance-snapshot.sh --notify 49 --channel email
```

### Complete Crontab Example

```cron
# OpenAI Admin CLI Automation
# Environment
OPENAI_ADMIN_KEY=sk-admin-...
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin

# Monitoring
0 8 * * * cd /path/to/openai-helper/examples && ./monitoring/daily-usage-report.sh --notify 49 --channel mattermost
0 9 * * 1 cd /path/to/openai-helper/examples && ./monitoring/weekly-cost-report.sh --notify 49 --channel email
0 10 1 * * cd /path/to/openai-helper/examples && ./monitoring/monthly-billing-summary.sh --notify 49 --channel email

# Security
0 2 * * * cd /path/to/openai-helper/examples && ./security/audit-security-scan.sh --notify 49 --channel email
0 23 * * 0 cd /path/to/openai-helper/examples && ./security/unused-keys-report.sh --days 60 --notify 49 --channel email
0 0 1 * * cd /path/to/openai-helper/examples && ./security/compliance-snapshot.sh --notify 49 --channel email
```

---

## Integration Examples

### Slack/Discord Integration

Adapt notification system or use webhooks:

```bash
#!/bin/bash
RESULT=$(./daily-usage-report.sh --format json)
curl -X POST "https://hooks.slack.com/..." \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Daily Usage Report Complete\", \"attachments\": [{\"text\": \"$RESULT\"}]}"
```

### CI/CD Pipeline

GitHub Actions example:

```yaml
name: Weekly Cost Report
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM
jobs:
  cost-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run cost report
        env:
          OPENAI_ADMIN_KEY: ${{ secrets.OPENAI_ADMIN_KEY }}
        run: |
          cd examples
          ./monitoring/weekly-cost-report.sh --format json > report.json
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: weekly-cost-report
          path: examples/report.json
```

### Custom Dashboard

Parse JSON output for visualization:

```python
import json
import subprocess

# Run report and get JSON
result = subprocess.run(
    ['./weekly-cost-report.sh', '--format', 'json'],
    capture_output=True,
    text=True
)
data = json.loads(result.stdout)

# Process and visualize
# ... your dashboard code here
```

---

## Best Practices

1. **Test First** - Run scripts manually before scheduling
2. **Start Conservative** - Begin with longer intervals (weekly), then increase
3. **Monitor Notifications** - Ensure alerts are reaching recipients
4. **Archive Reports** - Keep historical data for trend analysis
5. **Secure Credentials** - Use environment variables, never hardcode keys
6. **Review Regularly** - Act on findings from security scans
7. **Document Changes** - Note when you adjust thresholds or schedules

---

## Troubleshooting

### Script fails with "command not found"

Ensure CLI is accessible:
```bash
# Use absolute path or add to PATH
CLI_PATH="/full/path/to/openai_admin.py"
```

### No output or empty reports

Check API key permissions and network:
```bash
python3 openai_admin.py users list  # Test CLI directly
```

### Notification not received

Verify notification configuration:
```bash
python3 openai_admin.py notify status
python3 openai_admin.py notify test 49 --channel mattermost
```

### Cron job not running

Check cron logs and environment:
```bash
# View cron logs (macOS)
log show --predicate 'process == "cron"' --last 1h

# View cron logs (Linux)
grep CRON /var/log/syslog

# Test with explicit environment
0 8 * * * /usr/bin/env bash -c 'cd /path && export OPENAI_ADMIN_KEY=... && ./script.sh'
```

---

## Contributing

Have a useful script or improvement? Contributions welcome!

1. Follow existing script structure
2. Add comprehensive help text
3. Support notification options
4. Test on macOS and Linux
5. Document in this README

---

## Support

For issues or questions:
- **GitHub Issues**: [openai-admin-cli/issues](https://github.com/ADMIN-INTELLIGENCE-GmbH/openai-admin-cli/issues)
- **Email**: julian.billinger@admin-intelligence.com

---

## License

MIT License - See main project LICENSE file
