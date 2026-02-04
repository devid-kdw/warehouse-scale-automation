# Warehouse Scale Automation

Internal warehouse system for paint inventory management with staging/approval workflow and audit trail.

## Project Structure

```
warehouse-scale-automation/
├── backend/          # Flask API server
├── desktop-ui/       # Electron + React (future)
└── docs/             # Documentation
    ├── team/         # Team documentation (changelog, decisions, migrations)
    ├── status/       # Weekly status reports
    └── tasks/        # Task briefs
```

## Documentation

- **[Project Specification](./PROJECT_SPECIFICATION.md)** - Comprehensive technical specification
- **[Development Setup](./docs/team/DEVELOPMENT_SETUP.md)** - Step-by-step setup guide with troubleshooting
- **[Agent Instructions](./docs/team/AGENT_INSTRUCTIONS.md)** - Instructions for Frontend, Backend, and Testing agents
- **[Changelog](./docs/team/CHANGELOG.md)** - All changes tracked with test instructions
- **[Decisions](./docs/team/DECISIONS.md)** - Architectural and policy decisions
- **[Migrations](./docs/team/MIGRATIONS.md)** - Database schema evolution
- **[Release Checklist](./docs/team/RELEASE_CHECKLIST.md)** - Pre-release verification steps
- **[Status Reports](./docs/status/)** - Weekly progress updates

**For Testing Agent**:
- **[Testing Agent Rules](./docs/team/TESTING_AGENT_RULES.md)** - Testing protocol and responsibilities

## Quick Start

**For detailed setup instructions with troubleshooting**, see: **[Development Setup Guide](./docs/team/DEVELOPMENT_SETUP.md)**

### Backend (Terminal 1)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
flask db upgrade
flask seed
python3 run.py
```

Backend runs on: **http://localhost:5001**

### Desktop UI (Terminal 2)

```bash
cd desktop-ui
npm install
npm run electron:dev
```

## Tech Stack

- **Backend**: Python 3.11+, Flask, PostgreSQL
- **Desktop UI**: Electron + React (later phases)
- **API Docs**: OpenAPI/Swagger via flask-smorest

## License

Proprietary - Internal Use Only
