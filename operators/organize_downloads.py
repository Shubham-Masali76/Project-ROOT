import os
import shutil
import concurrent.futures
from pathlib import Path

# Separated Video and Audio for better mapping
CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".bmp", ".tiff"},
    "Documents": {".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".ppt", ".csv", ".rtf"},
    "Programs": {".exe", ".msi", ".bat", ".cmd", ".sh"},
    "Archives": {".zip", ".rar", ".tar", ".gz", ".7z", ".bz2"},
    "Video": {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"},
    "Audio": {".mp3", ".wav", ".flac", ".m4a", ".aac"},
    "Code": {".py", ".js", ".html", ".css", ".json", ".cpp", ".c", ".java", ".xml", ".sql", ".ts"}
}

def get_category(extension: str) -> str:
    """Returns the category folder name for a given extension."""
    extension = extension.lower()
    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category
    return "Others"

def execute():
    """Main execution function triggered by R.O.O.T."""
    user_home = Path.home()
    source_dir = user_home / "Downloads"
    
    if not source_dir.exists() or not source_dir.is_dir():
        return f"Error: The directory '{source_dir}' does not exist."

    print(f"[R.O.O.T Operator] Organizing folder: {source_dir}")
    
    # Map categories to absolute Windows Master Directories
    DESTINATIONS = {
        "Images": user_home / "Pictures" / "Saved Pictures", # Or just Pictures
        "Documents": user_home / "Documents",
        "Video": user_home / "Videos",
        "Audio": user_home / "Music",
        # Programs and Archives can stay in Downloads but neatly foldered
        "Programs": user_home / "Downloads" / "Programs",
        "Archives": user_home / "Downloads" / "Archives",
        "Code": user_home / "Documents" / "Code",
        "Others": user_home / "Downloads" / "Others"
    }
    
    moved_stats = {}
    moved_count = 0
    skipped_count = 0

    def move_file(item_name):
        nonlocal moved_count, skipped_count
        item = source_dir / item_name
        if not item.is_file():
            return
            
        extension = item.suffix
        category = get_category(extension)
        
        # Lookup the absolute target directory based on category
        category_dir = DESTINATIONS.get(category, user_home / "Downloads" / "Others")
        
        # Create the destination directory if it doesn't exist
        if not category_dir.exists():
            category_dir.mkdir(parents=True, exist_ok=True)
        
        target_file_path = category_dir / item.name
        
        # Prevent overwriting
        if target_file_path.exists():
            base_name = item.stem
            counter = 1
            while target_file_path.exists():
                target_file_path = category_dir / f"{base_name}_{counter}{extension}"
                counter += 1
        
        try:
            shutil.move(str(item), str(target_file_path))
            moved_count += 1
        except Exception as e:
            print(f"[R.O.O.T Error] moving {item.name}: {e}")
            skipped_count += 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(move_file, item.name) for item in source_dir.iterdir()]
        concurrent.futures.wait(futures)

    if moved_count == 0:
        result = "My sensors indicate your downloads folder is already clean."
    else:
        result = f"I have moved {moved_count} items to their respective master folders."
        
    print(f"[R.O.O.T Operator] {result} (Skipped {skipped_count})")
    return result

if __name__ == "__main__":
    execute()
