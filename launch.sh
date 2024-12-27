#!/bin/bash
set -e

CRON_INTERVAL=15

USERNAME=$(whoami)
echo "Found username: $USERNAME"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MAIN_PY="$SCRIPT_DIR/main.py"

if [ ! -f "$MAIN_PY" ]; then
    echo "Error: main.py not found in the current directory"
    exit 1
fi

echo "Found main.py at: $MAIN_PY"

chmod 755 "$MAIN_PY"
echo "Set executable permissions for main.py"

TEMP_CRON=$(mktemp)

crontab -r 2>/dev/null || true
echo "Cleared existing cron jobs"

echo "*/$CRON_INTERVAL * * * * /opt/homebrew/bin/python3 $MAIN_PY >> /tmp/firefoxbookmarkmonitor.log 2>> /tmp/firefoxbookmarkmonitor.error.log" >> "$TEMP_CRON"
crontab "$TEMP_CRON"
echo "Cron job added!"

rm "$TEMP_CRON"

echo "Setup complete: script will run every $CRON_INTERVAL minutes and log output to /tmp/firefoxbookmarkmonitor.log and errors to /tmp/firefoxbookmarkmonitor.error.log"
echo -e "\ncrontab -l:"
crontab -l
