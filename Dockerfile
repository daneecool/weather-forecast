FROM python:3-alpine

WORKDIR /app

# Install pip and requests
RUN apk add --no-cache py3-pip && pip3 install requests

# Copy your Python script
COPY src/preprocess.py /app/src/preprocess.py

# Copy cron job
COPY cronjob /var/spool/cron/crontabs/root
RUN chmod 0644 /var/spool/cron/crontabs/root

# Create log file to be able to run tail
# RUN touch /var/log/cron.log

# Run cron in the foreground and tail the log
CMD crond -l 1 -f
