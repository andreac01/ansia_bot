# Use the requested Python 3.13 image
FROM python:3.13-slim

# Install necessary system utilities
RUN apt-get update && apt-get install -y \
    cron \
    git \
    tzdata \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Force the container to use Rome time
ENV TZ="Europe/Rome"

WORKDIR /root/ansia_bot

# Recreate the exact virtual environment path your scripts expect
RUN mkdir -p /root/.venv && \
    python3 -m venv /root/.venv/telegram_venv

# Install dependencies
COPY requirements.txt .
RUN /root/.venv/telegram_venv/bin/pip install --upgrade pip && \
    /root/.venv/telegram_venv/bin/pip install -r requirements.txt

# Copy your application code (from the root context)
COPY . .

# Ensure scripts are executable
RUN chmod +x *.sh

# Setup cron jobs for 2 AM (update) and 8 AM (main)
RUN echo "0 2 * * * root /root/ansia_bot/auto_update.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/ansia-cron && \
    echo "0 8 * * * root /root/ansia_bot/main.sh >> /var/log/cron.log 2>&1" >> /etc/cron.d/ansia-cron && \
    chmod 0644 /etc/cron.d/ansia-cron && \
    crontab /etc/cron.d/ansia-cron

# Grab the entrypoint from the deployment folder
COPY deployment/entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh

RUN touch /var/log/cron.log nohup.out

ENTRYPOINT ["/root/entrypoint.sh"]