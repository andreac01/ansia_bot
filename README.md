# Ansia Bot

## Description

A Telegram bot designed to handle collaborative pads (HedgeDoc) and notify teams of upcoming and missed deadlines. The bot is actively used by the Politecnico Open unix Labs (POuL) student association to manage task tracking for their courses.

The codebase is divided into two primary execution flows:
* `main.py`: Executed periodically (via cron job) to scrape tracked pads and automatically send notifications about upcoming tasks (today/tomorrow) and overdue tasks to registered Telegram chats.
* `request_handler.py`: Runs continuously to provide an interactive Telegram interface. It handles adding/removing tracked pads, managing admins, registering chats for updates, and generating standardized Markdown templates for new courses.

## Commands

* `/start` or `/help`: Display the help message with available commands.
* `/check`: Manually trigger a check for tasks and send notifications to the current chat.
* `/get_pads`: View the list of currently active tracked pads.
* `/create_pad`: Start an interactive wizard to generate the Markdown boilerplate for a new course pad and its social media links.
* `/add_pad [url]`: Add a new published CodiMD/HedgeDoc pad to the tracking list *(Admin required)*.
* `/remove_pad [url]`: Remove a pad from the tracking list *(Admin required)*.
* `/get_paduli`: View the list of "paduled" people (assigned roles/users).
* `/padula [role] [old_username] [new_username]`: Reassign a role to a new user. Use `_` as a dummy user to add/remove without replacement *(Admin required)*.
* `/add_chat`: Register the current chat to receive daily automatic update notifications *(Admin required)*.
* `/remove_chat`: Unregister the current chat from receiving daily updates *(Admin required)*.
* `/add_admin [tg_username]`: Grant admin privileges to a new user *(Admin required)*.

## File Organization

```text
ansia_bot/
├── admins.json                # List of bot admins (Telegram usernames)
├── auto_update.sh             # Script to pull git updates and restart the bot
├── core/                      # Core logic and utilities
│   ├── scraper.py             # Scrapes HedgeDoc/CodiMD pads
│   └── utils.py               # Data processing, text generation, and Jinja2 rendering
├── data/                      # Local cached copies of the traced markdown pads
├── deployment/                # Docker deployment files
│   ├── docker-compose.yml     # Docker Compose configuration
│   ├── Dockerfile             # Docker image build instructions
│   └── entrypoint.sh          # Container entrypoint and service initialization
├── main.py                    # Script to broadcast daily notifications
├── main.sh                    # Shell wrapper to execute main.py via cron
├── padulati.json              # List of roles and tagged users for templates
├── politamtam_dates.json      # Timetable configuration for PoliTamTam releases
├── README.md                  # This file
├── request_handler.py         # Main Telegram bot interface loop
├── requirements.txt           # Python dependencies
├── settings.json              # Bot configuration (Token, tracked URLs, chat IDs)
└── templates/                 # Jinja2 templates
    ├── corso                  # Template for course task lists
    └── links                  # Template for generated course links
```

## Setup & Deployment

Before starting, message [@BotFather](https://t.me/botfather) on Telegram to create a bot and get your unique Bot Token.
If you are a POuL member you can ask @andrea_cer for the current token.

### Method 1: Docker (Recommended)

The easiest way to deploy the bot is via Docker Compose. The provided configuration automatically sets up the Python environment, dependencies, and internal cron jobs for daily notifications.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/andreac01/ansia_bot.git
   cd ansia_bot
   ```
2. **Configure your settings:**
   Edit `settings.json` and insert your Bot Token under the `"token"` key. Ensure your Telegram username is listed in `admins.json`.
3. **Start the container:**
   ```bash
   cd deployment
   docker-compose up -d --build
   ```
   *Note: The `docker-compose.yml` automatically mounts your local JSON configuration files and the `data/` directory into the container, ensuring persistent state across restarts.*

### Method 2: Manual Local Setup

If you prefer running the bot natively on your host machine:

1. **Clone and setup the virtual environment:**
   ```bash
   git clone https://github.com/andreac01/ansia_bot.git
   cd ansia_bot
   mkdir -p ~/.venv
   python3 -m venv ~/.venv/telegram_venv
   source ~/.venv/telegram_venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
2. **Configure Settings:**
   Add your token to `settings.json` and your username to `admins.json`. Update the paths inside `main.sh` and `auto_update.sh` to match your local repository location.
   Now they point to `/root/ansia_bot` to match the location inside the docker container.
3. **Run the interactive bot:**
   ```bash
   nohup python3 request_handler.py > nohup.out 2>&1 &
   ```
4. **Set up Cron Jobs:**
   To enable automatic updates and daily notifications, add the following to your crontab (`crontab -e`):
   ```cron
   # Daily git pull and bot restart
   0 4 * * * /absolute/path/to/ansia_bot/auto_update.sh
   # Daily notification broadcast
   0 8 * * * /absolute/path/to/ansia_bot/main.sh
   ```

## Workflow & Important Notes

1. **Initial Access:** Start the bot in Telegram. Ensure your username is in `admins.json` so you can use the `/add_chat` and `/add_pad` commands.
2. **Register Chats:** Add the bot to your target group chat and run `/add_chat` to register it for automated daily summaries.
3. **Track Pads:** HedgeDoc pads MUST be **Published** as **Editable** for the scraper to successfully read them. Add the published link using `/add_pad`.
4. **Roles/Padulati:** Keep `padulati.json` updated via the `/padula` command so the template generator correctly tags the responsible team members.