FROM python:3.11-slim-bullseye

WORKDIR /app

# Install cron and upgrade all packages to reduce vulnerabilities
RUN apt-get update && apt-get install -y cron && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY src/ /app/src
COPY cronjob /etc/cron.d/cronjob

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cronjob

# Apply cron job
RUN crontab /etc/cron.d/cronjob

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

CMD ["cron", "-f"]