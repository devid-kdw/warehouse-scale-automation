# Development Setup Guide

This document provides step-by-step instructions for setting up the development environment.

---

## Prerequisites

- Python 3.9+
- Node.js 18+ (for desktop UI)
- PostgreSQL 14+
- Git

---

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd "/Users/grzzi/Desktop/Paint Manager/warehouse-scale-automation/backend"
```

### 2. Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate venv (macOS/Linux)
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### 3. Install Dependencies

```bash
# Use pip3 (not pip) to ensure correct Python version
pip3 install -r requirements.txt

# Optional: Upgrade pip if you see warnings
python3 -m pip install --upgrade pip
```

**Note**: If you see "Defaulting to user installation" warning, it's safe to ignore. Dependencies will install correctly.

### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env
```

Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret for JWT tokens (generate random string)
- `API_TOKEN` - API access token

### 5. Initialize Database

```bash
# Run migrations
flask db upgrade

# Seed initial data (creates location, users, articles)
flask seed
```

### 6. Start Backend Server

```bash
# Use python3 (not python)
python3 run.py
```

Server will start on: **http://127.0.0.1:5001**

---

## Desktop UI Setup

### 1. Navigate to Desktop UI Directory

```bash
cd "/Users/grzzi/Desktop/Paint Manager/warehouse-scale-automation/desktop-ui"
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Backend URL

Edit `desktop-ui/.env` (or create if missing):

```
VITE_API_URL=http://localhost:5001
VITE_API_TOKEN=your_api_token_from_backend_env
```

### 4. Start Desktop UI

```bash
npm run electron:dev
```

Electron app will launch with UI connected to backend.

---

## Running Both Together

### Option 1: Two Terminals (Recommended)

**Terminal 1 - Backend**:
```bash
cd "/Users/grzzi/Desktop/Paint Manager/warehouse-scale-automation/backend"
source venv/bin/activate
python3 run.py
```

**Terminal 2 - UI**:
```bash
cd "/Users/grzzi/Desktop/Paint Manager/warehouse-scale-automation/desktop-ui"
npm run electron:dev
```

### Option 2: Single Terminal (Background + Foreground)

```bash
# Start backend in background
cd "/Users/grzzi/Desktop/Paint Manager/warehouse-scale-automation/backend" && source venv/bin/activate && python3 run.py &

# Start UI in foreground
cd "/Users/grzzi/Desktop/Paint Manager/warehouse-scale-automation/desktop-ui" && npm run electron:dev
```

**To stop background process**: `jobs` → `kill %1`

---

## Troubleshooting

### "command not found: pip"

**Solution**: Use `pip3` instead of `pip` on macOS.

```bash
pip3 install -r requirements.txt
```

### "command not found: python"

**Solution**: Use `python3` instead of `python`.

```bash
python3 run.py
```

### "ModuleNotFoundError: No module named 'flask'"

**Cause**: Virtual environment not activated or dependencies not installed.

**Solution**:
```bash
# Make sure venv is activated (you should see (venv) in prompt)
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt
```

### Virtual Environment Not Working

**Solution**: Recreate venv from scratch.

```bash
# Deactivate if active
deactivate

# Remove old venv
rm -rf venv

# Create new venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt
```

### Database Connection Errors

**Check**:
1. PostgreSQL is running: `psql --version`
2. Database URL is correct in `.env`
3. Database exists: `psql -l | grep warehouse`

**Create database if missing**:
```bash
createdb warehouse
```

### Port 5001 Already in Use

**Solution**: Kill process on port 5001 or change port in `backend/app/config.py`.

```bash
# Find process on port 5001
lsof -i :5001

# Kill it
kill -9 <PID>
```

---

## Verification

### Backend Health Check

```bash
curl http://localhost:5001/api/health
```

Expected response:
```json
{"status": "healthy", "database": "connected"}
```

### Swagger UI

Open in browser: **http://localhost:5001/swagger-ui**

### Login to UI

Default credentials (after `flask seed`):
- **Admin**: username: `stefan`, password: _(check seed data)_
- **Operator**: username: `operator`, password: _(check seed data)_

---

## Development Workflow

1. **Start Backend** (Terminal 1)
2. **Start UI** (Terminal 2)
3. **Make changes** in code
4. **Backend auto-reloads** (Flask debug mode)
5. **UI requires manual refresh** (Ctrl+R in Electron) or restart

---

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest
```

### Frontend Build Test

```bash
cd desktop-ui
npm run build
```

---

## Common Paths Reference

```
Project Root: /Users/grzzi/Desktop/Paint Manager/warehouse-scale-automation

Backend:
  - Code: ./backend/app/
  - Tests: ./backend/tests/
  - Migrations: ./backend/migrations/versions/
  - Config: ./backend/app/config.py
  - Entry: ./backend/run.py

Desktop UI:
  - Code: ./desktop-ui/src/
  - Components: ./desktop-ui/src/components/
  - Pages: ./desktop-ui/src/pages/
  - API: ./desktop-ui/src/api/
  - Entry: ./desktop-ui/src/main.tsx

Documentation:
  - Team Docs: ./docs/team/
  - Status Reports: ./docs/status/
  - Task Briefs: ./docs/tasks/
```

---

Last Updated: 2026-02-04
