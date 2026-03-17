# Setup Guide - Nike Bot Commercial

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (npm)
- **Rust 1.70+** (for Tauri compilation)
- **Visual Studio Build Tools** (Windows only - C++ build tools)

## Environment Setup

### 1. Clone / Copy Project

```bash
git clone <your-repo>
cd nike-bot-commercial
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your values:
- `STRIPE_SECRET_KEY` - Get from Stripe dashboard
- `API_SECRET` - Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### 3. Backend Setup (Your Friend's Task)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
python main.py
```

Backend should run on `http://localhost:8000`

### 4. Frontend/Desktop Setup (Your Task)

```bash
cd app
npm install
npm run tauri dev  # Development mode
```

This will open the app in development with hot reload.

## Development Workflow

### Terminal 1: Backend
```bash
cd backend
venv\Scripts\activate
python main.py
# Runs on localhost:8000
```

### Terminal 2: Frontend
```bash
cd app
npm run tauri dev
# Opens dev window with hot reload
```

## Building for Release

### 1. Frontend Build
```bash
cd app
npm run tauri build
```

Output: `app/src-tauri/target/release/nike-bot-commercial.exe`

### 2. Deploy Backend
See [DEPLOYMENT.md](./DEPLOYMENT.md) for server setup.

## Testing Token Flow

### 1. Generate Test Token

```bash
cd backend
python -c "
from routes.auth import *
import datetime
payload = {
    'email': 'test@example.com',
    'plan': 'pro',
    'iat': datetime.datetime.utcnow(),
    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
}
token = jwt.encode(payload, 'dev-secret-key', algorithm='HS256')
print(token)
"
```

### 2. Test in App

1. Launch frontend: `npm run tauri dev`
2. Paste token in dialog
3. Should show Dashboard if valid

## Troubleshooting

### Issue: Rust compilation fails
**Solution:** Install Visual Studio Build Tools with C++ option
```bash
# Windows
https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
```

### Issue: Port 8000 already in use
**Solution:** Change in `.env` and `tauri.conf.json`
```
API_PORT=8001
```

### Issue: Token validation always fails
**Solution:** Check API is running
```bash
curl -s http://localhost:8000/health
# Should return {"status": "healthy"}
```

### Issue: Can't paste token in dialog
**Solution:** Check browser console (F12) for errors
