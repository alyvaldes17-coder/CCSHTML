import os
import json
import base64
import sqlite3
import shutil
import tempfile
import win32crypt  # type: ignore[import-untyped]
from Crypto.Cipher import AES  # pip install pycryptodome

PROFILE_PATH = r"C:/Users/beriann/Documents/Repos/nike/chrome_profiles/bot_9222"
OUTPUT = "cookies_extracted.json"

TARGET_DOMAINS = [
    "nike.cl",
    ".nike.cl",
    "www.nike.cl",
    "checkout.vtex.com",
    ".checkout.vtex.com",
    "vtex.com",
]


def get_chrome_key():
    """Extract Chrome AES key from Local State."""
    local_state_path = os.path.join(PROFILE_PATH, "Local State")

    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)

    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]


def decrypt_cookie(encrypted_value, key):
    """Decrypt Chrome AES-GCM cookie."""
    try:
        if encrypted_value.startswith(b"v10") or encrypted_value.startswith(b"v11"):
            iv = encrypted_value[3:15]
            payload = encrypted_value[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt(payload)[:-16]
            return decrypted.decode()
        else:
            return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode()
    except:
        return None


def find_cookie_db(path):
    for dirpath, _, filenames in os.walk(path):
        if "Cookies" in filenames:
            return os.path.join(dirpath, "Cookies")
    return None


def extract():
    key = get_chrome_key()

    cookie_path = find_cookie_db(PROFILE_PATH)
    print(f"🟢 AES Key OK")
    print(f"🟢 Cookie DB: {cookie_path}")

    # -------------------------
    # 🔥 FIX: copiar archivo Cookies a temp
    # -------------------------
    temp_cookie = os.path.join(tempfile.gettempdir(), "Cookies_temp.db")
    shutil.copy2(cookie_path, temp_cookie)

    # abrir copia desbloqueada
    conn = sqlite3.connect(temp_cookie)
    cursor = conn.cursor()
    cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
    rows = cursor.fetchall()
    conn.close()

    result = {}
    for host, name, enc in rows:
        if not any(domain in host for domain in TARGET_DOMAINS):
            continue
        value = decrypt_cookie(enc, key)
        result[name] = value

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print("🔥 Cookies desencriptadas → cookies_extracted.json")


if __name__ == "__main__":
    extract()
