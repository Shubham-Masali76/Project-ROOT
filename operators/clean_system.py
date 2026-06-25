import os
import shutil
import concurrent.futures
import ctypes

def clean_directory(directory_path):
    deleted = 0
    skipped = 0
    if not directory_path or not os.path.exists(directory_path):
        return deleted, skipped
    
    with os.scandir(directory_path) as entries:
        for entry in entries:
            try:
                if entry.is_file() or entry.is_symlink():
                    os.unlink(entry.path)
                elif entry.is_dir():
                    shutil.rmtree(entry.path)
                deleted += 1
            except Exception:
                skipped += 1
    return deleted, skipped

def empty_recycle_bin():
    try:
        # 7 = SHERB_NOCONFIRMATION (1) + SHERB_NOPROGRESSUI (2) + SHERB_NOSOUND (4)
        result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
        return result == 0
    except Exception:
        return False

def execute():
    user_temp = os.environ.get('TEMP')
    system_temp = r'C:\Windows\Temp'
    
    # Threaded Cleaner Engine
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        f1 = executor.submit(clean_directory, user_temp)
        f2 = executor.submit(clean_directory, system_temp)
        f3 = executor.submit(empty_recycle_bin)
        
        t1, s1 = f1.result()
        t2, s2 = f2.result()
        rb_success = f3.result()
        
    total_deleted = t1 + t2
    total_skipped = s1 + s2
    
    result_text = f"I have wiped {total_deleted} temporary files from your system."
    if rb_success:
        result_text += " I also emptied your recycle bin."
        
    print(f"[R.O.O.T Operator] {result_text} (Skipped {total_skipped} locked files)")
    return result_text
