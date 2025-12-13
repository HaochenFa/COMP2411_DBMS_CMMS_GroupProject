# Gemini Agent Guide for PolyU CMMS

This document guides AI agents on how to safely and effectively work on the PolyU Campus Maintenance and Management System (CMMS).

## 1. Project Overview

PolyU CMMS is a database-driven application for managing campus maintenance, activities, personnel, and facilities. It features a React frontend, Flask backend, MySQL database, and an Electron desktop wrapper.

**Key Components:**

- **Frontend:** React (Vite), Recharts, Lucide React.
- **Backend:** Python (Flask), mysql-connector-python.
- **Database:** MySQL 8.0.
- **Desktop:** Electron.
- **Deployment:** Docker Compose or local shell scripts (`run.sh`/`run.ps1`).

## 2. Architecture & Tech Stack

### Backend (`/backend`)

- **Framework:** Flask.
- **Database Driver:** `mysql-connector-python`.
- **Port:** 5050 (Note: standard Flask is 5000, but this project uses **5050**).
- **Key Files:**
  - `app.py`: Main application logic and API endpoints.
  - `db.py`: Database connection and initialization logic.
  - `schema.sql`: Database schema definition (DESTRUCTIVE: contains `DROP TABLE`).
  - `requirements.txt`: Python dependencies.

### Frontend (`/frontend`)

- **Framework:** React 19 + Vite.
- **State Management:** React Context (`RoleContext`) + Local State.
- **Port:** 5173.
- **Key Files:**
  - `src/App.jsx`: Main entry point and routing.
  - `src/components/`: specialized UI components (Dashboard, EntityManager, etc.).
  - `vite.config.js`: Build configuration.

### Database (`/backend/schema.sql`)

- **Type:** Relational (MySQL).
- **Core Entities:** Person, Profile, School, Location, Activity, Maintenance, Participation, Affiliation.
- **Key Constraint:** `init_db()` and `schema.sql` will **WIPE ALL DATA** when run.

## 3. Operational Guidelines

### ⚠️ Critical Safety Warnings

1.  **Database Reset:** The `init_db` function (triggered by `db_init.py` or startup checks) uses `backend/schema.sql`, which drops all tables. **NEVER** run this unless you intend to delete all data.
2.  **Raw SQL:** The `/api/query` endpoint and `DevConsole.jsx` allow raw SQL execution. Be extremely careful when generating or modifying code related to this feature to prevent SQL injection or accidental data loss.
3.  **Port Conflicts:** Backend runs on **5050**. Ensure `API_URL` in frontend matches this port.

### Development Workflow

1.  **Start the App:**
    - **Recommended:** `./run.sh` (macOS/Linux) or `.\run.ps1` (Windows).
    - **Docker:** `docker-compose up --build`.
2.  **Verify Status:**
    - Backend Health: `http://localhost:5050/api/health`
    - Frontend: `http://localhost:5173`

### Testing

Always run relevant tests after changes.

- **Backend (pytest):**

  ```bash
  cd backend
  # Run unit tests (fast)
  pytest tests/ --ignore=tests/integration
  # Run all tests (requires running DB)
  pytest tests/
  ```

- **Frontend (Vitest):**

  ```bash
  cd frontend
  npm test -- --run
  ```

- **Desktop:**
  ```bash
  cd desktop
  npm test -- --run
  ```

## 4. Coding Conventions

- **Style:** Follow existing indentation (4 spaces for Python, 2 spaces for JS/JSON).
- **Naming:**
  - Python: `snake_case` for functions/vars, `PascalCase` for classes.
  - JS: `camelCase` for functions/vars, `PascalCase` for React components.
  - SQL: `snake_case` for tables and columns.
- **Comments:** Explain _why_, not _what_.
- **API Design:** RESTful. Use standard HTTP methods (GET, POST, PUT, DELETE). return JSON.

## 5. Common Tasks & Snippets

### Adding a New Entity

1.  **Update Schema:** Add `CREATE TABLE` in `backend/schema.sql`.
2.  **Update Backend:** Add endpoints in `backend/app.py`.
3.  **Update Frontend:** Create a new manager component or update `EntityManager.jsx`.
4.  **Add Tests:** Add `tests/test_api_new_entity.py`.

### Modifying the Dashboard

1.  **Backend:** Add a new report endpoint in `backend/app.py` under `# --- Advanced Report Endpoints ---`.
2.  **Frontend:** Update `frontend/src/components/Dashboard.jsx` to fetch and display the new data.

### Troubleshooting

- **"Database connection failed"**: Check if MySQL container is running or if local MySQL credentials in `.env` (or `db.py` defaults) are correct.
- **CORS Errors**: Ensure `flask-cors` is initialized in `app.py`.

## 6. Safety Net & Restricted Operations

AI agents must strictly adhere to the following rules to prevent damage and ensure system integrity.

### 🚫 Restricted Actions (DO NOT PERFORM)

1.  **Destructive Database Calls:**
    - **NEVER** run `python backend/db_init.py` or call `init_db()` unless the user _explicitly_ asks to "reset" or "wipe" the database.
    - **NEVER** run `python backend/seed_data.py` without user confirmation, as it truncates tables.
2.  **File Deletion:**
    - **NEVER** delete or modify the logic of `run.sh`, `run.ps1`, `docker-compose.yml`, or `GEMINI.md` unless tasked to fix them.
3.  **Security Bypasses:**
    - **NEVER** remove the "Dangerous Operation" warning modal in `DevConsole.jsx`.
    - **NEVER** disable the role-based access checks (e.g., `role === 'Admin'`) in frontend components.
4.  **Credential Exposure:**
    - **NEVER** hardcode passwords or API keys in source code. Always use `os.getenv` or `.env` files.

### ⚠️ Mandatory Guidelines

1.  **UI/UX Consistency:**
    - **Theme:** Strictly adhere to the PolyU color scheme: Red Wine (`#A6192E`) and Beige/Gold (`#B08E55`).
    - **Libraries:** Do **not** install new UI libraries (e.g., MUI, Tailwind, Bootstrap) without permission. Use existing CSS modules and inline styles.
2.  **Testing Requirements:**
    - If you modify backend logic, you **MUST** run `pytest tests/`.
    - If you modify frontend components, you **MUST** run `npm test`.
3.  **Schema Integrity:**
    - If you modify `backend/schema.sql`, you **MUST** warn the user that applying changes requires a database reset/migration.

---

_Generated by Gemini Agent._
