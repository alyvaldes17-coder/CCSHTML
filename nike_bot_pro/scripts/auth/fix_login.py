#!/usr/bin/env python3
"""Script para refactorizar ui/app.py"""

with open('ui/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar _login
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if 'def _login(self, account_name: str, account_path: str):' in line:
        start_idx = i
    elif start_idx != -1 and line.strip().startswith('def ') and i > start_idx + 1:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    # Nueva función _login
    new_login = """    def _login(self, account_name: str, account_path: str):
        \"\"\"Fire-and-forget LOGIN - open Chrome, user logs in manually.\"\"\"
        print(f"[UI] Opening Chrome for LOGIN {account_name}...")
        
        def do_login():
            try:
                from auth.session_check import open_chrome_for_login
                open_chrome_for_login(account_path, account_name)
            except Exception as e:
                print(f"[UI] ERROR LOGIN: {e}")
        
        thread = threading.Thread(target=do_login, daemon=True)
        thread.start()
        print(f"[UI] Chrome opened - Login manually and close when done")

"""
    
    new_lines = lines[:start_idx] + [new_login] + lines[end_idx:]
    
    with open('ui/app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("OK - _login replaced")
else:
    print(f"ERROR - _login not found (start={start_idx}, end={end_idx})")
