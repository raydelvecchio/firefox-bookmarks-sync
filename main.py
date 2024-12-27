import time
import os
import subprocess
import sqlite3
import http.client
import urllib.parse
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import re
import plistlib

BOOKMARK_TOOLBAR_FOLDER_NAME = "R"
ICLOUD_BOOKMARKS_PATH = "Library/Mobile Documents/com~apple~CloudDocs/Bookmarks"
FIREFOX_PROFILES_FOLDER = "Library/Application Support/Firefox/Profiles"
PDF_PATTERS = [
    r'\.pdf$',
    r'^https://arxiv\.org/pdf/'
]
SLEEP_SECONDS = 1
PRINT_MEMORY_SECONDS = 60
SHOULD_PRINT_MEMORY = False

def get_memory_usage():
    """Gets memory usage of this process without any external imports."""
    pid = os.getpid()
    
    try:
        cmd = f'ps -o rss= -p {pid}'
        output = subprocess.check_output(cmd.split()).decode()
        return int(output.strip()) / 1024  # convert KB to MB
    except:
        return 0 

class FirefoxBookmarkHandler(FileSystemEventHandler):
    def __init__(self):
        self.home = Path.home()
        self.icloud_path = self.home / ICLOUD_BOOKMARKS_PATH
        
        self.icloud_path.mkdir(parents=True, exist_ok=True)
        
        firefox_profiles = self.home / FIREFOX_PROFILES_FOLDER
        print(f"Looking for Firefox profiles in: {firefox_profiles}")
        
        try:
            profiles = list(firefox_profiles.glob("*.default-release*"))  # have seen both .default-release and .default-release-1, both in same directory, so must check for both!
            if not profiles:  # if no default-release profile found, try listing all profiles
                profiles = list(firefox_profiles.glob("*"))
                print(f"Available profiles: {[p.name for p in profiles]}")
                
            valid_profiles = [p for p in profiles if (p / "places.sqlite").exists()]
            
            if not valid_profiles:
                raise Exception("No Firefox profile found with places.sqlite")
            
            default_profile = valid_profiles[0]
            if len(valid_profiles) > 1:
                print(f"Multiple profiles found with places.sqlite. Using: {default_profile}")
            
            print(f"Found Firefox profile: {default_profile}")
            
            self.places_db = default_profile / "places.sqlite"
            if not self.places_db.exists():
                raise Exception(f"places.sqlite not found at {self.places_db}")
            
            print(f"Found places.sqlite at: {self.places_db}")
            
        except Exception as e:
            print(f"Error setting up Firefox profile: {e}")
            raise
                
        self.log_existing_bookmarks()

    def log_existing_bookmarks(self):
        """Logs count of existing bookmarks upon startup."""
        try:
            temp_db = Path("/tmp/places_temp.sqlite")  # connect to a copy of the database to avoid locks
            with open(self.places_db, "rb") as src, open(temp_db, "wb") as dst:
                dst.write(src.read())

            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()

            query = """
                SELECT COUNT(*) as bookmark_count
                FROM moz_bookmarks
                JOIN moz_places ON moz_bookmarks.fk = moz_places.id
                WHERE moz_bookmarks.parent IN (
                    SELECT id FROM moz_bookmarks 
                    WHERE title = ? AND parent = 3
                )
            """  # query count of bookmarks in our designated bookmarks toolbar folder name
            
            cursor.execute(query, (BOOKMARK_TOOLBAR_FOLDER_NAME,))
            bookmark_count = cursor.fetchone()[0]
            
            if bookmark_count > 0:
                print(f"Found {bookmark_count} existing bookmarks in '{BOOKMARK_TOOLBAR_FOLDER_NAME}' folder")
            else:
                print(f"NO EXISTING bookmarks found in '{BOOKMARK_TOOLBAR_FOLDER_NAME}' folder")

            conn.close()
            temp_db.unlink()

        except Exception as e:
            print(f"Error logging existing bookmarks: {e}")

    def on_modified(self, event):
        """If the watchdog detects a path is modified, then this is triggered."""
        if Path(event.src_path) == self.places_db:
            self.check_new_bookmarks()

    def check_new_bookmarks(self):        
        """Checks Firefox database for new bookmarks."""
        try:
            temp_db = Path("/tmp/places_temp.sqlite")  # again, copy to avoid locks
            with open(self.places_db, "rb") as src, open(temp_db, "wb") as dst:
                dst.write(src.read())

            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()

            query = """
                SELECT moz_places.url, moz_bookmarks.dateAdded/1000000 as date_added, moz_bookmarks.title
                FROM moz_bookmarks
                JOIN moz_places ON moz_bookmarks.fk = moz_places.id
                WHERE moz_bookmarks.parent IN (
                    SELECT id FROM moz_bookmarks 
                    WHERE title = ? AND parent = 3
                )
                ORDER BY date_added DESC
                LIMIT 1  -- get the most recently added one
            """  # get all bookmarks in the folder ordered by date, and just the last one
            
            cursor.execute(query, (BOOKMARK_TOOLBAR_FOLDER_NAME,))
            recent_bookmarks = cursor.fetchall()
            
            for url, _, title in recent_bookmarks:
                print(f"New bookmark detected: {title} - {url}")
                self.handle_url(url, title)

            conn.close()
            temp_db.unlink()

        except Exception as e:
            print(f"Error processing bookmarks: {e}")

    def handle_url(self, url: str, title: str):
        """What happens to the new URL that we find. Do we download and save a PDF, or save the URL?"""
        try:
            if any(re.search(pattern, url, re.IGNORECASE) for pattern in PDF_PATTERS):
                self.download_pdf(url, title)
            else:
                self.save_url(url, title)
        except Exception as e:
            print(f"Error handling URL {url}: {e}")

    def download_pdf(self, url: str, title: str):
        """Downloads the PDF if the link saved is a PDF link. Names it the title."""
        try:
            parsed_url = urllib.parse.urlparse(url)
            conn = http.client.HTTPSConnection(parsed_url.netloc)
            conn.request("GET", parsed_url.path + "?" + parsed_url.query)
            response = conn.getresponse()
            
            if response.status == 200:
                filename = f"{title}.pdf"
                filepath = self.icloud_path / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.read())
                
                print(f"Downloaded PDF: {filename}")
            conn.close()
        except Exception as e:
            print(f"Error downloading PDF {url}: {e}")

    def save_url(self, url: str, title: str):
        """Saves the URL as the title, but as a webloc file that we can open with a browser."""
        try:
            filename = f"{title}.webloc"
            filepath = self.icloud_path / filename
            
            plist_content = {
                'URL': url
            }
            
            with open(filepath, 'wb') as f:
                plistlib.dump(plist_content, f, fmt=plistlib.FMT_XML)
            
            print(f"Saved .webloc shortcut: {filename}")
        except Exception as e:
            print(f"Error saving URL {url}: {e}")

def main():
    print("Starting bookmark handler")
    
    event_handler = FirefoxBookmarkHandler()
    observer = Observer()
    
    firefox_dir = event_handler.places_db.parent
    
    observer.schedule(event_handler, str(firefox_dir), recursive=False)  # start the observer on the Firefox directory
    observer.start()

    try:
        seconds_counter = 0
        while True:
            if SHOULD_PRINT_MEMORY:
                if seconds_counter >= PRINT_MEMORY_SECONDS:
                    memory_usage = get_memory_usage()
                    print(f"Current memory usage: {memory_usage:.2f} MB")
                    seconds_counter = 0
            time.sleep(SLEEP_SECONDS)
            if SHOULD_PRINT_MEMORY:
                seconds_counter += SLEEP_SECONDS
    except KeyboardInterrupt:
        observer.stop()
        print("Bookmark handler stopped")

    observer.join()

if __name__ == "__main__":
    main()
