#!/bin/bash

# 1. Start the cron daemon in the background
service cron start

# 2. Execute scripts on boot
echo "Executing auto-update on boot..."
/root/ansia_bot/auto_update.sh

echo "Executing main check on boot..."
/root/ansia_bot/main.sh

# 3. Keep the container alive and pipe logs to Docker stdout
# This allows you to see what the bot is doing when you run `docker logs`
tail -f /var/log/cron.log /root/ansia_bot/nohup.out