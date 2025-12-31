import os
import shutil
import sys
import subprocess

SOURCE_DIR = r"c:\Users\kevin\.gemini\antigravity\scratch\ker_solutions\ker_saas"
DEST_DIR = r"c:\Users\kevin\.gemini\antigravity\scratch\ker_saas_final_v1"

def log(msg):
    print(f"[MIGRATION] {msg}")

def copy_project():
    if os.path.exists(DEST_DIR):
        log(f"Destination {DEST_DIR} already exists. Removing it to ensure clean slate...")
        try:
            shutil.rmtree(DEST_DIR)
        except Exception as e:
            log(f"Error removing existing destination: {e}")
            return False

    log(f"Copying from {SOURCE_DIR} to {DEST_DIR}...")
    
    # Ignore patterns to skip heavy/temp files
    ignore_patterns = shutil.ignore_patterns(
        "venv", "__pycache__", "*.pyc",         # Python junk
        ".git", ".idea", ".vscode",             # IDE/Git junk
        "build", ".dart_tool",                  # Flutter build artifacts
        ".gradle", "local.properties",          # Android build artifacts
        "Pods", "DerivedData"                   # iOS build artifacts
    )

    try:
        shutil.copytree(SOURCE_DIR, DEST_DIR, ignore=ignore_patterns)
        log("Copy complete.")
        return True
    except Exception as e:
        log(f"Copy failed: {e}")
        return False

def setup_backend():
    backend_dir = os.path.join(DEST_DIR, "backend")
    log("Setting up Backend...")
    
    # Check if we need to update any hardcoded paths in .env (if it exists)
    env_file = os.path.join(backend_dir, ".env")
    if os.path.exists(env_file):
        log("Checking .env for hardcoded paths...")
        # (Simple pass-through for now, usually just keys)

    # Re-create Setup Script for automation
    setup_script = os.path.join(backend_dir, "SETUP_AND_RUN.bat")
    with open(setup_script, "w") as f:
        f.write(f"""@echo off
cd /d "{backend_dir}"
if not exist venv (
    echo Creating venv...
    python -m venv venv
)
call venv\\Scripts\\activate
echo Installing dependencies...
pip install -r requirements.txt
pip install uvicorn fastapi sqlalchemy[asyncio] aiosqlite python-jose[cryptography] passlib[bcrypt] python-multipart google-generativeai
echo Starting Server...
uvicorn main:app --reload --host 0.0.0.0 --port 8000
""")
    
    # Execute Setup via subprocess detached? No, user will run it. 
    # But we want to auto-setup.
    log("Backend setup script created.")

def setup_frontend():
    frontend_dir = os.path.join(DEST_DIR, r"frontend\ker_app")
    log("Setting up Frontend...")
    
    # Re-create Setup Script
    setup_script = os.path.join(frontend_dir, "SETUP_AND_RUN.bat")
    with open(setup_script, "w") as f:
        f.write(f"""@echo off
set "PATH=%PATH%;C:\\Users\\kevin\\flutter\\bin"
cd /d "{frontend_dir}"
echo Running flutter clean...
call flutter clean
echo Running flutter pub get...
call flutter pub get
echo Starting Chrome...
call flutter run -d chrome --web-renderer html
""")
    log("Frontend setup script created.")

if __name__ == "__main__":
    if copy_project():
        setup_backend()
        setup_frontend()
        log("MIGRATION SUCCESSFUL! New project ready at: " + DEST_DIR)
    else:
        log("MIGRATION FAILED.")
