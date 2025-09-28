# Telegram Job Notification Bot

A Telegram bot that sends real-time job notifications based on user-defined keywords. The bot polls an external job API periodically and delivers personalized job alerts to subscribed users.

## Features

- **Keyword-based job filtering**: Users can set custom search keywords for job matching
- **Real-time notifications**: Jobs are fetched periodically and sent immediately to relevant users
- **User management**: Track user preferences, activity, and subscription status
- **Dual database support**: Local SQLite for development, remote Turso for production
- **External API integration**: Connects to OLJ Scraper API for job data

## Requirements

- Python 3.8+
- External job scraper API [OLJ Scraper](https://github.com/kenBinary/olj-scraper)
- Telegram Bot Token
- SQLite (local) or Turso (production) database

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd tg-job-notif-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Setup

### Database Setup

Create database tables:
```bash
python -m scripts.create_tables --dev   # Local SQLite
python -m scripts.create_tables --prod  # Remote Turso
```

Remove tables (cleanup):
```bash
python -m scripts.table_cleanup --dev   # Local SQLite
python -m scripts.table_cleanup --prod  # Remote Turso
```

Seed database with sample data:
```bash
python -m scripts.seed_db --dev   # Local SQLite
python -m scripts.seed_db --prod  # Remote Turso
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Required: Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Required: External API Configuration
API_BASE_URL=http://localhost:8000

# Required for Production: Turso Database
TURSO_DATABASE_URL=libsql://your-database-url.turso.io
TURSO_AUTH_TOKEN=your_turso_auth_token
```

## Usage

### Development Mode (Local SQLite)
```bash
python main.py --dev
```

### Production Mode (Remote Database)
```bash
python main.py --prod
```

### Default Mode (Development)
```bash
python main.py
```

## CLI Options

- `--dev`: Run in development mode with local SQLite database
- `--prod`: Run in production mode with remote Turso database
- `--help`: Display help information

## Configuration

### Job Notification Settings
- **Polling Interval**: 60 seconds (configurable in `main.py`)
- **Job Limit**: 30 jobs per fetch (configurable in `send_job_notification.py`)
- **Message Delay**: 1.5 seconds between job notifications to prevent rate limiting

### Database Configuration
- **Local**: SQLite database stored in `data/tg-job-bot.db`
- **Remote**: Turso database with connection URL and auth token
- **Models**: User profiles, job tracking, and conversation states

### Logging Configuration
- **Level**: INFO
- **Format**: `%(asctime)s [%(levelname)-8s]: %(message)s`
- **Output**: Console logging for all operations

## Integration/External Services

### OLJ Scraper API
The bot integrates with an external job scraper API that must be running separately:

- **Health Check**: `/health` endpoint validation on startup
- **Job Fetching**: Retrieves jobs with keyword filtering and pagination
- **Base URL**: Configurable via `API_BASE_URL` environment variable
- **Default**: `http://localhost:8000`

### Telegram Bot API
- **Token**: Required in environment variables
- **Commands**: `/start`, `/stop`, `/cancel`
- **Message Handling**: Keyword input and job notifications

## Example Command

```bash
python main.py --dev

# Bot interaction flow:
# 1. User sends /start to the bot
# 2. Bot asks for job keywords
# 3. User responds: "python, react, remote"
# 4. Bot confirms setup and begins monitoring
# 5. Every 60 seconds, bot checks for new jobs
# 6. Matching jobs are sent as notifications
```

## Scripts

### Database Management
```bash
python -m scripts.create_tables --dev     # Local development
python -m scripts.create_tables --prod    # Production

# Remove all database tables
python -m scripts.table_cleanup --dev     # Local development
python -m scripts.table_cleanup --prod    # Production

# Seed database with sample data
python -m scripts.seed_db --dev           # Local development
python -m scripts.seed_db --prod          # Production
```

### Bot Operations
```bash
python main.py --dev                      # Development mode
python main.py --prod                     # Production mode
```

## TODO

- [ ] Implement getting the jobs via webhooks instead of requesting resource every minute
- [ ] Make this available to public
    - [ ] Service to deactive users if no activity in a week
