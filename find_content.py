import os

search_dirs = [
    r"c:\Users\kevin\.gemini\antigravity\scratch\ker_solutions",
    r"C:\Users\kevin\.gemini\antigravity\brain\fe321be3-b559-4c2e-8505-e68c4414eeae"
]

keywords = ["marketing", "redes", "fases", "plan de", "5 fases"]

print(f"Searching for keywords: {keywords}")

files_found = 0

for root_dir in search_dirs:
    if not os.path.exists(root_dir):
        continue
        
    for subdir, dirs, files in os.walk(root_dir):
        # Skip noisy dirs
        if any(x in subdir for x in ['node_modules', '.git', 'venv', '__pycache__', 'site-packages', 'build', '.dart_tool']):
            continue
            
        for file in files:
            if not file.endswith(('.md', '.txt', '.json')):
                continue
                
            filepath = os.path.join(subdir, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    
                    found_keywords = [Kw for Kw in keywords if Kw in content]
                    if found_keywords:
                        print(f"[MATCH] {file} (Keywords: {found_keywords})")
                        print(f"   Path: {filepath}")
                        files_found += 1
            except Exception:
                pass

if files_found == 0:
    print("No matches found.")
