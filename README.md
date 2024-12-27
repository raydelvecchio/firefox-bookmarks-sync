# Bookmarks Sync
Every time I add a bookmark to a folder in Firefox, I want to add it to an iCloud as well, auto downloading the PDF if there is any. This is so I can use my iPad as a reading devine. System program to monitor this!

# Notes
* Firefox maintains bookmarks in a SQLite file, located at `/Users/<USER>/Library/Application Support/Firefox/Profiles`, in a folder that looks like `23gbxgg0.default-release-1`, always containing `default-release`
    * Stores them in the User's Library so if uninstalled the data perserveres
* To access iCloud storage from the file system, you must navigate to `/Users/<User>/Library/Mobile Documents/com~apple~CloudDocs`
    * Cloud Docs is what is shown when you click `iCloud` on the file system in Mac
* In the `places.sql` database Firefox maintains, any bookmark in the toolbar has a parent ID of `3`
