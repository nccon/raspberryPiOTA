# auto_updater.py
import os
import sys
import urllib.request
import re

# --- Configuration ---
VERSION_FILE_URL = "https://yourserver.com/OTA/latest_version.txt"
SCRIPT_FILE_URL = "https://yourserver.com/OTA/latest_script.txt"  # .txt on server
TARGET_SCRIPT = "main_script.py"  # saved locally as .py

def parse_version(version_str):
    return tuple(map(int, version_str.strip().split(".")))

def get_remote_version():
    try:
        with urllib.request.urlopen(VERSION_FILE_URL) as response:
            return response.read().decode('utf-8').strip()
    except Exception as e:
        print(f"[Updater] Failed to fetch remote version: {e}")
        return None

def get_local_version(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        match = re.search(r'__version__\s*=\s*[\'"](\d+\.\d+\.\d+)[\'"]', content)
        return match.group(1) if match else None
    except Exception as e:
        print(f"[Updater] Failed to read local version: {e}")
        return None

def update_script(local_path, remote_version):
    try:
        print(f"[Updater] Downloading version {remote_version} from {SCRIPT_FILE_URL}...")
        with urllib.request.urlopen(SCRIPT_FILE_URL) as response:
            new_code = response.read()

        backup_path = local_path + ".bak"
        os.rename(local_path, backup_path)

        with open(local_path, "wb") as f:
            f.write(new_code)

        print("[Updater] Update complete. Restarting script...")
        os.execv(sys.executable, ['python'] + sys.argv)

    except Exception as e:
        print(f"[Updater] Update failed: {e}")

def check_for_updates():
    local_path = os.path.join(os.path.dirname(__file__), TARGET_SCRIPT)

    local_version = get_local_version(local_path)
    remote_version = get_remote_version()

    if not remote_version or not local_version:
        print("[Updater] Skipping update check (version info unavailable)")
        return

    print(f"[Updater] Local version: {local_version}, Remote version: {remote_version}")

    if parse_version(remote_version) > parse_version(local_version):
        update_script(local_path, remote_version)
    else:
        print("[Updater] No update needed.")
