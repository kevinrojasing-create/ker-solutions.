import os
import time

search_dirs = [
    r"c:\Users\kevin\.gemini\antigravity\scratch\ker_solutions",
    r"C:\Users\kevin\.gemini\antigravity\brain\fe321be3-b559-4c2e-8505-e68c4414eeae"
]

now = time.time()
two_hours_ago = now - (20 * 3600) # Extended to 20 hours just in case of timezone/drift, user said "2 hours" but safety first.

print(f"Searching for files modified since {time.ctime(two_hours_ago)}")

found_any = False
for root_dir in search_dirs:
    if not os.path.exists(root_dir):
        continue
        
    for subdir, dirs, files in os.walk(root_dir):
        # Skip node_modules, .git, venv to reduce noise
        if 'node_modules' in subdir or '.git' in subdir or 'venv' in subdir or '__pycache__' in subdir:
            continue
            
        for file in files:
            filepath = os.path.join(subdir, file)
            try:
                mtime = os.path.getmtime(filepath)
                if mtime > two_hours_ago:
                    print(f"[MODIFIED] {time.ctime(mtime)} | {filepath}")
                    found_any = True
            except Exception as e:
                pass

if not found_any:
    print("No recent files found.")
