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
- **[Changelog](./docs/team/CHANGELOG.md)** - All changes tracked with test instructions
- **[Decisions](./docs/team/DECISIONS.md)** - Architectural and policy decisions
- **[Migrations](./docs/team/MIGRATIONS.md)** - Database schema evolution
- **[Release Checklist](./docs/team/RELEASE_CHECKLIST.md)** - Pre-release verification steps
- **[Status Reports](./docs/status/)** - Weekly progress updates

## Quick Start

See [PROJECT_SPECIFICATION.md](./PROJECT_SPECIFICATION.md) for detailed documentation.

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python run.py
```

## Tech Stack

- **Backend**: Python 3.11+, Flask, PostgreSQL
- **Desktop UI**: Electron + React (later phases)
- **API Docs**: OpenAPI/Swagger via flask-smorest

## License

Proprietary - Internal Use Only
