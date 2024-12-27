# Bookmarks Sync
Every time I add a bookmark to a folder in Firefox, I want to add it to an iCloud as well, auto downloading the PDF if there is any. This is so I can use my iPad as a reading devine.

# Features
* All in vanilla python, no external imports needed
* Customizable routes, target folders, and refresh times

# Notes
* Firefox maintains bookmarks in a SQLite file, located at `/Users/<USER>/Library/Application Support/Firefox/Profiles`, in a folder that looks like `23gbxgg0.default-release-1`, always containing `default-release`
    * Stores them in the User's Library so if uninstalled the data perserveres
* To access iCloud storage from the file system, you must navigate to `/Users/<User>/Library/Mobile Documents/com~apple~CloudDocs`
    * Cloud Docs is what is shown when you click `iCloud` on the file system in Mac
* In the `places.sql` database Firefox maintains, any bookmark in the toolbar has a parent ID of `3`
* This only works if iCloud is set to auto download on your target devices
    * You can turn this on for specific folders by opening the files all on the device, holding down, and pressing `Keep Downloaded`
    * Not only will not *not* remove those files, but it will also automatically download them when connected to internet, which is ideal!

# Deprecated
I used to be a dumbass, and tried to write a whole `launchctl` process that will startup and monitor the files for changes then sync upon change. Then I realized I'm an idiot. And I can just write a script and use Cron for this.
* Commands to manage the running Mac process:
    * `./launch.sh`: load the process to autorestart and lauch!
    * `cat /tmp/firefoxbookmarkmonitor.log`: print the logs from the bookmark monitor
    * `cat /tmp/firefoxbookmarkmonitor.error.log`: print the error logs from the bookmark monitor
    * `launchctl list | grep firefoxbookmarkmonitor`: find the launch item from the list of launch processes
