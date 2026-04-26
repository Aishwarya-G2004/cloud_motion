import requests
import os
import time
import re
from pathlib import Path

USERNAME    = "ashishbgoyal24@gmail.com"    # ← your MOSDAC email
PASSWORD    = "Nitinsir@124"            # ← your MOSDAC password
SAVE_DIR    = r"D:\Insat_data\raw"
FOLDER_PATH = "/Order/Apr26_178218"
BASE_URL    = "https://mosdac.gov.in"

Path(SAVE_DIR).mkdir(parents=True, exist_ok=True)
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

# ── Login ──────────────────────────────────────────────────────────────
print("Logging in...")
resp       = session.get(f"{BASE_URL}/download/", allow_redirects=True)
action_url = re.search(r'action="([^"]+)"', resp.text).group(1).replace("&amp;","&")
login_resp = session.post(action_url, data={
    "username": USERNAME, "password": PASSWORD, "credentialId": ""
}, allow_redirects=True)
print(f"Login final URL: {login_resp.url}")

# ── Find correct API URL by trying all known endpoints ─────────────────
print("\nProbing API endpoints...")
candidates = [
    f"{BASE_URL}/download/api/list?path={FOLDER_PATH}",
    f"{BASE_URL}/download/?cd=%2FOrder%2FApr26_178218&api=list",
    f"{BASE_URL}/uops/download/api/list?path={FOLDER_PATH}",
    f"{BASE_URL}/download/api/files?path={FOLDER_PATH}",
    f"{BASE_URL}/download/listdir?path={FOLDER_PATH}",
    f"{BASE_URL}/download/api?action=list&path={FOLDER_PATH}",
    f"https://download.mosdac.gov.in/api/list?path={FOLDER_PATH}",
]

for url in candidates:
    try:
        r = session.get(url, timeout=10)
        preview = r.text[:100].replace("\n","")
        print(f"[{r.status_code}] {url}")
        print(f"         Preview: {preview}")
        print()
    except Exception as e:
        print(f"[ERR] {url} — {e}")

# ── Also check what the download page's network calls look like ────────
print("\nChecking download page source for API hints...")
page = session.get(f"{BASE_URL}/download/", allow_redirects=True)
# Look for API URLs in the page source
api_hints = re.findall(r'(api[^"\'<>\s]{0,60})', page.text)
unique_hints = list(set(api_hints))[:20]
print("API patterns found in page source:")
for h in unique_hints:
    print(f"  {h}")