# Firefox Bookmarks Sync
Every time I add a bookmark to a folder in Firefox, I want to add it to an iCloud as well, auto downloading the PDF if there is any. This is so I can use my iPad as a reading devine.

# Features
* All in vanilla python, no external imports needed aside from building
* Customizable routes, target folders, and refresh times
* Cron for low memory overhead
* Fully buildable to an executable

# Run Instructions
1. Ensure iCloud sync is enabled on your target devices. On your iPad, go to Settings > [Your Name] > iCloud > iCloud Drive and make sure it's turned on.For the specific folder where bookmarks are synced, open the Files app, navigate to the folder, press down, and enable `Keep Downloaded` to ensure automatic syncing for offline viewing.
2. Configure `main.py` with all the config in your local setup, such as input and output directories.
3. `pip3 install -r requirements.txt` to install build dependencies, preferably in a venv.
4. `python3 build.py` to build the executable. This will appear in `/dist`.
5. `chmod +x launch.sh`
6. `./launch.sh` to start the cron job on your machine to periodically sync your bookmarks!
7. Run `cat /tmp/firefoxbookmarkmonitor.log` to ensure your sync is working as expected!

# Notes
* Firefox maintains bookmarks in a SQLite file, located at `/Users/<USER>/Library/Application Support/Firefox/Profiles`, in a folder that looks like `23gbxgg0.default-release-1`, always containing `default-release`
    * Stores them in the User's Library so if uninstalled the data perserveres
* To access iCloud storage from the file system, you must navigate to `/Users/<User>/Library/Mobile Documents/com~apple~CloudDocs`
    * Cloud Docs is what is shown when you click `iCloud` on the file system in Mac
* In the `places.sql` database Firefox maintains, any bookmark in the toolbar has a parent ID of `3`
* This only works if iCloud is set to auto download on your target devices
    * You can turn this on for specific folders by opening the files all on the device, holding down, and pressing `Keep Downloaded`
    * Not only will not *not* remove those files, but it will also automatically download them when connected to internet, which is ideal!
* Commands:
    * `cat /tmp/firefoxbookmarkmonitor.log`: print the logs from the bookmark monitor
    * `cat /tmp/firefoxbookmarkmonitor.error.log`: print the error logs from the bookmark monitor

# Deprecated
I used to be a dumbass, and tried to write a whole `launchctl` process that will startup and monitor the files for changes then sync upon change. Then I realized I'm an idiot. And I can just write a script and use Cron for this.
* Commands to manage the running Mac process:
    * `./launch.sh`: load the process to autorestart and lauch!
    * `launchctl list | grep firefoxbookmarkmonitor`: find the launch item from the list of launch processes
