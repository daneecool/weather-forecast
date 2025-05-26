FROM ubuntu:22.04

WORKDIR /app

# Install Python, pip, and cron
RUN apt-get update && \
    apt-get install -y python3 python3-pip cron nano && \
    pip3 install requests

# Copy your Python script
COPY src/preprocess.py /app/src/preprocess.py

# Copy the cronjob file
COPY cronjob /etc/cron.d/cronjob

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cronjob

# Create log file to be able to run tail
RUN touch /var/log/cron.log

# Run cron in the foreground and tail the log
CMD cron && tail -f /var/log/cron.log
