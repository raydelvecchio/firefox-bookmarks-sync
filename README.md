# Bookmarks Sync
Every time I add a bookmark to a folder in Firefox, I want to add it to an iCloud as well, auto downloading the PDF if there is any. This is so I can use my iPad as a reading devine. System program to monitor this!

# Features
* All in vanilla python, no external imports needed
* Customizable routes, target folders, and refresh times
* Auto sync bookmarks upon startup that are not saved
* Launch script at `./launch.sh` that adds the script as a MAC launch agent to auto startup when your compute is active!

# Notes
* Firefox maintains bookmarks in a SQLite file, located at `/Users/<USER>/Library/Application Support/Firefox/Profiles`, in a folder that looks like `23gbxgg0.default-release-1`, always containing `default-release`
    * Stores them in the User's Library so if uninstalled the data perserveres
* To access iCloud storage from the file system, you must navigate to `/Users/<User>/Library/Mobile Documents/com~apple~CloudDocs`
    * Cloud Docs is what is shown when you click `iCloud` on the file system in Mac
* In the `places.sql` database Firefox maintains, any bookmark in the toolbar has a parent ID of `3`
* This only works if iCloud is set to auto download on your target devices
    * You can turn this on for specific folders by opening the files all on the device, holding down, and pressing `Keep Downloaded`
    * Not only will not *not* remove those files, but it will also automatically download them when connected to internet, which is ideal!
