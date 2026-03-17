import json
import os

# ════════════════════════════════════════════════════════════════════
# PATHS ABSOLUTAS (fuente única de verdad)
# ════════════════════════════════════════════════════════════════════
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
AUTH_ROOT = os.path.join(PROJECT_ROOT, "auth")

# Chrome executables (en orden de preferencia)
CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

CHROME_PATH = None
for path in CHROME_PATHS:
    if os.path.exists(path):
        CHROME_PATH = path
        break

# ════════════════════════════════════════════════════════════════════
# SETTINGS JSON
# ════════════════════════════════════════════════════════════════════
SETTINGS_JSON = os.path.join(os.path.dirname(__file__), "settings.json")

with open(SETTINGS_JSON, "r", encoding="utf-8") as f:
    _cfg = json.load(f)

# Exportar valores como variables Python
BASE_URL = _cfg["base_url"]
SKU = _cfg["sku"]
SELLER = _cfg["seller"]
HEADLESS = _cfg["headless"]
PROFILE_PATH = _cfg["PROFILE_PATH"]
TIMEOUT_SECONDS = _cfg["timeout_seconds"]
LOG_LEVEL = _cfg["log_level"]
