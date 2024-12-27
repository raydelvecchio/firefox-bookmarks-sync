#!/bin/bash

USERNAME=$(whoami)
echo "Found username: $USERNAME"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MAIN_PY="$SCRIPT_DIR/main.py"

if [ ! -f "$MAIN_PY" ]; then
    echo "Error: main.py not found in the current directory"
    exit 1
fi

echo "Found main.py at: $MAIN_PY"

PLIST_PATH="$HOME/Library/LaunchAgents/com.$USERNAME.firefoxbookmarkmonitor.plist"
PLIST_CONTENT="<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
    <key>Label</key>
    <string>com.$USERNAME.firefoxbookmarkmonitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$MAIN_PY</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/firefoxbookmarkmonitor.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/firefoxbookmarkmonitor.error.log</string>
</dict>
</plist>"

echo "$PLIST_CONTENT" > "$PLIST_PATH"
echo "Created launch agent plist at: $PLIST_PATH"

chmod 644 "$PLIST_PATH"
echo "Set correct permissions for plist file"

launchctl load "$PLIST_PATH"
echo "Loaded launch agent"

echo "Setup completed successfully!"
