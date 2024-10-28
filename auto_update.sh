#!/bin/bash

# Navigate to the directory containing main.py
cd <base_directory>/ansia_bot
# Pull the latest changes from the remote repository
git pull origin master
# Activate the virtual environment
source ~/venvs/telegram_venv/bin/activate
# Install any new dependencies
pip install -r requirements.txt
# Kill the existing Python process
pkill -f request_handler.py
# Run the Python script
nohup python3 request_handler.py &
