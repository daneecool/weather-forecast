# Use a base image with a Linux distro, here we use Ubuntu
FROM ubuntu:latest

# Install cron and other necessary packages
RUN apt-get update && apt-get install -y cron python3-pip

# install requests package using pip
RUN pip3 install requests

# Copy your cron file into the container
COPY cronjob /etc/cron.d/cronjob

# Give execution rights on the cron job file
RUN chmod 0644 /etc/cron.d/cronjob

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Do NOT run: RUN crontab /etc/cron.d/cronjob
# Run the cron service and tail the log file
CMD cron && tail -f /var/log/cron.log