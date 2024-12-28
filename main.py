import sqlite3
import http.client
import urllib.parse
from pathlib import Path
import re
import plistlib
import datetime

BOOKMARK_TOOLBAR_FOLDER_NAME = "R"
ICLOUD_BOOKMARKS_PATH = "/Users/raydelv/Library/Mobile Documents/com~apple~CloudDocs/Bookmarks"
FIREFOX_PROFILES_FOLDER = "/Users/raydelv/Library/Application Support/Firefox/Profiles"
PDF_PATTERS = [
    r'\.pdf$',
    r'^https://arxiv\.org/pdf/'
]

def log(message):
    """Prints a message to console with the current date/time, up to the second."""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] {message}")

def init_sync():
    """Initializes and starts syncing the bookmarks in the desired bookmark folder to iCloud."""
    log("Starting Firefox bookmark sync...")
    icloud_path = Path(ICLOUD_BOOKMARKS_PATH)
    icloud_path.mkdir(parents=True, exist_ok=True)
    
    firefox_profiles = Path(FIREFOX_PROFILES_FOLDER)
    log(f"Looking for Firefox profiles in: {firefox_profiles}")
    
    try:
        profiles = list(firefox_profiles.glob("*.default-release*"))  # have seen both .default-release and .default-release-1, both in same directory, so must check for both!
        if not profiles:  # if no default-release profile found, try listing all profiles
            profiles = list(firefox_profiles.glob("*"))
            log(f"Available profiles: {[p.name for p in profiles]}")
            
        valid_profiles = [p for p in profiles if (p / "places.sqlite").exists()]
        
        if not valid_profiles:
            raise Exception("No Firefox profile found with places.sqlite")
        
        default_profile = valid_profiles[0]
        if len(valid_profiles) > 1:
            log(f"Multiple profiles found with places.sqlite. Using: {default_profile}")
        
        log(f"Found Firefox profile: {default_profile}")
        
        places_db = default_profile / "places.sqlite"
        if not places_db.exists():
            raise Exception(f"places.sqlite not found at {places_db}")
        
        log(f"Found places.sqlite at: {places_db}")
        
    except Exception as e:
        log(f"Error setting up Firefox profile: {e}")
        raise
            
    log_existing_bookmarks(places_db)
    sync_all_bookmarks(places_db, icloud_path)

def log_existing_bookmarks(places_db):
    """Logs count of existing bookmarks upon startup."""
    try:
        temp_db = Path("/tmp/places_temp.sqlite")  # connect to a copy of the database to avoid locks
        with open(places_db, "rb") as src, open(temp_db, "wb") as dst:
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
            log(f"Found {bookmark_count} existing bookmarks in '{BOOKMARK_TOOLBAR_FOLDER_NAME}' folder")
        else:
            log(f"NO EXISTING bookmarks found in '{BOOKMARK_TOOLBAR_FOLDER_NAME}' folder")

        conn.close()
        temp_db.unlink()

    except Exception as e:
        log(f"Error logging existing bookmarks: {e}")

def sync_all_bookmarks(places_db, icloud_path):
    """Syncs all bookmarks from the target folder to the drive and removes files from the drive that don't have matching bookmarks."""
    try:
        temp_db = Path("/tmp/places_temp.sqlite")
        with open(places_db, "rb") as src, open(temp_db, "wb") as dst:
            dst.write(src.read())

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        query = """
            SELECT moz_places.url, moz_bookmarks.title
            FROM moz_bookmarks
            JOIN moz_places ON moz_bookmarks.fk = moz_places.id
            WHERE moz_bookmarks.parent IN (
                SELECT id FROM moz_bookmarks 
                WHERE title = ? AND parent = 3
            )
        """
        
        cursor.execute(query, (BOOKMARK_TOOLBAR_FOLDER_NAME,))
        bookmarks = cursor.fetchall()
        
        bookmark_titles = set(title for _, title in bookmarks)
        existing_files = set(f.stem for f in icloud_path.iterdir() if f.is_file())
        
        new_bookmarks = [(url, title) for url, title in bookmarks if title not in existing_files]
        log(f"Syncing {len(new_bookmarks)} new bookmarks...")
        for url, title in new_bookmarks:
            handle_url(url, title, icloud_path)
        
        files_to_remove = existing_files - bookmark_titles
        log(f"Removing {len(files_to_remove)} files without matching bookmarks...")
        for file_name in files_to_remove:
            file_path = next(icloud_path.glob(f"{file_name}.*"))
            file_path.unlink()
            log(f"Removed file: {file_path.name}")

        conn.close()
        temp_db.unlink()
        log("Bookmark sync completed.")

    except Exception as e:
        log(f"Error syncing all bookmarks: {e}")

def handle_url(url: str, title: str, icloud_path: Path):
    """Handles the new URL by either downloading a PDF or saving the URL."""
    try:
        if any(re.search(pattern, url, re.IGNORECASE) for pattern in PDF_PATTERS):
            download_pdf(url, title, icloud_path)
        else:
            save_url(url, title, icloud_path)
    except Exception as e:
        log(f"Error handling URL {url}: {e}")

def download_pdf(url: str, title: str, icloud_path: Path):
    """Downloads the PDF if the link saved is a PDF link. Names it the title."""
    try:
        parsed_url = urllib.parse.urlparse(url)
        conn = http.client.HTTPSConnection(parsed_url.netloc)
        conn.request("GET", parsed_url.path + "?" + parsed_url.query)
        response = conn.getresponse()
        
        if response.status == 200:
            filename = f"{title}.pdf"
            filepath = icloud_path / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.read())
            
            log(f"Downloaded PDF: {filename}")
        conn.close()
    except Exception as e:
        log(f"Error downloading PDF {url}: {e}")

def save_url(url: str, title: str, icloud_path: Path):
    """Saves the URL as the title, but as a webloc file that we can open with a browser."""
    try:
        filename = f"{title}.webloc"
        filepath = icloud_path / filename
        
        plist_content = {
            'URL': url
        }
        
        with open(filepath, 'wb') as f:
            plistlib.dump(plist_content, f, fmt=plistlib.FMT_XML)
        
        log(f"Saved .webloc shortcut: {filename}")
    except Exception as e:
        log(f"Error saving URL {url}: {e}")

def main():    
    init_sync()

if __name__ == "__main__":
    main()
