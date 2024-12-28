#!/bin/bash
set -e

CRON_INTERVAL_MINUTES=15
USERNAME=$(whoami)
echo "Found username: $USERNAME"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EXECUTABLE="$SCRIPT_DIR/dist/firefox_bookmark_monitor"

if [ ! -f "$EXECUTABLE" ]; then
    echo "Error: firefox_bookmark_monitor executable not found in dist directory"
    exit 1
fi

echo "Found executable at: $EXECUTABLE"
chmod 755 "$EXECUTABLE"
echo "Set executable permissions for firefox_bookmark_monitor"

TEMP_CRON=$(mktemp)
crontab -r 2>/dev/null || true
echo "Cleared existing cron jobs"

: > /tmp/firefoxbookmarkmonitor.log
: > /tmp/firefoxbookmarkmonitor.error.log
echo "Cleared existing log files"

echo "*/$CRON_INTERVAL_MINUTES * * * * $EXECUTABLE >> /tmp/firefoxbookmarkmonitor.log 2>> /tmp/firefoxbookmarkmonitor.error.log" >> "$TEMP_CRON"
crontab "$TEMP_CRON"
echo "Cron job added!"

rm "$TEMP_CRON"
echo "Setup complete: script will run every $CRON_INTERVAL_MINUTES minutes"
echo -e "\ncrontab -l:"
crontab -l

echo "Running firefox_bookmark_monitor for the first time..."
$EXECUTABLE >> /tmp/firefoxbookmarkmonitor.log 2>> /tmp/firefoxbookmarkmonitor.error.log
echo "Initial run complete. Check logs for details."
echo "To view logs, run: cat /tmp/firefoxbookmarkmonitor.log"
