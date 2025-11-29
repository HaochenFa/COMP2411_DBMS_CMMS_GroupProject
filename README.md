# PolyU CMMS - Campus Maintenance and Management System

A comprehensive database-driven application for managing campus maintenance, activities, personnel, and facilities at The Hong Kong Polytechnic University. Developed for COMP2411 Database Systems course.

## Features

### Core Functionality

- **Executive Dashboard**: Real-time visualization of maintenance tasks, people distribution, activities, and school statistics with interactive charts
- **Entity Management**: Full CRUD operations for:
  - **People** - Personnel records with supervisor hierarchies
  - **Schools** - Academic departments with faculty affiliations
  - **Locations** - Campus buildings, floors, and rooms
  - **Activities** - Events and lectures with organizers
  - **Maintenance** - Maintenance tasks with chemical tracking
- **Relationship Management**:
  - **Participations** - Person-Activity relationships
  - **Affiliations** - Person-School relationships
- **Safety Search**: Search for cleaning activities with chemical hazards by building location
- **Dev Console**: Full SQL query interface with:
  - Support for all SQL operations (SELECT, INSERT, UPDATE, DELETE, etc.)
  - Warning popup for dangerous operations before execution
  - Query history with localStorage persistence
- **Data Import/Export**:
  - CSV bulk import for batch data operations
  - CSV bulk export for all entity and relationship tables
  - Date-stamped export files with proper CSV escaping

### Technical Features

- **Electron Desktop App**: Standalone desktop application with integrated backend and frontend
- **Docker Support**: Fully containerized deployment with MySQL, Flask backend, and React frontend
- **PolyU Themed UI**: Red wine and white color scheme matching PolyU branding
- **Responsive Design**: Modern, compact layout with glass panel effects
- **Data Visualization**: Interactive charts using Recharts library
- **Cascading Selects**: Smart form fields with dependent dropdowns and ability to add new entries

## Prerequisites

### For quick start (recommended)

- Docker Desktop (Windows/macOS) with Docker Compose v2 (the `docker compose` command)
- Node.js (with npm) for running the Electron desktop app

### For manual setup (no Docker)

- Python 3.8+
- Conda (e.g. Miniconda/Anaconda or Mambaforge)
- (Optional) [uv](https://github.com/astral-sh/uv) for fast Python package & virtual env management
- Node.js 16+
- MySQL Server

### Installing Docker

#### Windows & macOS (Docker Desktop)

1. Download Docker Desktop from <https://docs.docker.com/desktop/>.
2. Run the installer and follow the prompts.
3. Start Docker Desktop (it must be running in the background).
4. Verify that Docker works in a new terminal:

   ```bash
   docker --version
   docker info
   ```

   The `docker info` command should print details about your Docker engine. If it reports that it cannot connect, make sure Docker Desktop is running.

#### Linux (Docker Engine)

Docker installation varies by distribution. The most reliable source is the official docs: <https://docs.docker.com/engine/install/>.

As a rough guide for Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker "$USER"  # Optional: run docker without sudo
```

After installation, log out and back in if you changed group membership, then verify:

```bash
docker --version
docker info
```

### Installing Node.js

1. Go to <https://nodejs.org/> and download the latest **LTS** release for your platform.
2. Install it using the platform installer.
3. Verify in a new terminal:

   ```bash
   node --version
   npm --version
   ```

On macOS/Linux you can also use a version manager like [`nvm`](https://github.com/nvm-sh/nvm) if you prefer.

> **Note:** The `run.sh` / `run.ps1` scripts will check that both Docker and Node.js are installed and that Docker is running before starting the app.

## Setup & Running

### Option A: Desktop app (Electron + Docker, recommended)

1. Ensure Docker Desktop is installed and running.
2. Ensure Node.js (with npm) is installed from <https://nodejs.org/>.
3. From the project root, run (macOS/Linux):

    ```bash
    ./run.sh
    ```

   Or from Windows PowerShell:

    ```powershell
    .\run.ps1
    ```

4. The script will:
   - Launch the Electron desktop app.
   - On first run, install the Node/Electron dependencies in the `desktop/` folder.
   - The Electron app will start the Dockerized MySQL, backend, and frontend stack.
   - Once the UI is ready, it will appear directly in the desktop window (no external browser needed).

### Option B: Manual setup (no Docker)

#### 1. Database Setup

Ensure your MySQL server is running. Create a database (default name `cmms_db`) or let the initialization script do it.

#### 2. Backend (Flask)

1. Navigate to the project root.
2. Create and activate a Conda environment (recommended):

    ```bash
    # Create the environment (adjust python version if needed)
    conda create -n cmms-env python=3.11 -y

    # Activate it
    conda activate cmms-env
    ```

3. Install backend dependencies (pick one of the following):

    **Using pip (standard):**

    ```bash
    pip install -r backend/requirements.txt
    ```

    **Using uv (faster, if installed):**

    ```bash
    # Inside the activated conda env
    uv pip install -r backend/requirements.txt
    ```

    > If you prefer, you can also have uv manage the virtual environment entirely:
    >
    > ```bash
    > uv venv .venv
    > source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    > uv pip install -r backend/requirements.txt
    > ```
    >
    > In that case you don’t need Conda; just make sure a compatible Python (3.8+) is available.

4. Configure environment variables:
    Create a `.env` file in the `backend` directory (or root, depending on how you run it, but `db.py` loads from current working dir usually).

    ```env
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=your_password
    DB_NAME=cmms_db
    ```

5. Initialize the database (DESTRUCTIVE RESET):
 Run this from the **project root** when you want to create or completely
 reset the schema as defined in `backend/schema.sql`:

 ```bash
 python backend/db_init.py
 ```

6. Run the server:
    Run this from the **backend** directory:

    ```bash
    cd backend
    python app.py
    ```

    The backend will start on `http://localhost:5000`.

#### 3. Frontend (Vite + React)

1. Navigate to the `frontend` directory:

    ```bash
    cd frontend
    ```

2. Install dependencies:

    ```bash
    npm install
    ```

3. Run the development server:

    ```bash
    npm run dev
    ```

     The frontend will start on `http://localhost:5173` (usually).

     > **Note:** In the Docker/Electron setup, the React app is configured to talk to the backend at
     > `http://localhost:5050/api`. If you run the backend manually on port `5000` instead, update the
     > `API_URL` constant in `frontend/src/App.jsx` to `http://localhost:5000/api` so the frontend can
     > reach your manually started backend.

## Project Structure

```text
.
├── backend/                 # Flask REST API backend
│   ├── app.py               # Main Flask application with API endpoints
│   ├── db.py                # Database connection utilities
│   ├── db_init.py           # Database initialization script
│   ├── schema.sql           # Database schema definition
│   ├── seed_data.py         # Mock data generation script
│   ├── wait_for_db.py       # Docker database readiness check
│   ├── Dockerfile           # Backend container configuration
│   └── requirements.txt     # Python dependencies
│
├── frontend/                # React + Vite frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── Dashboard.jsx           # Executive dashboard with charts
│   │   │   ├── EntityManager.jsx       # Generic CRUD with import/export
│   │   │   ├── RelationshipManager.jsx # Relationship management with export
│   │   │   ├── SafetySearch.jsx        # Chemical hazard search
│   │   │   ├── DevConsole.jsx          # SQL query interface with warnings
│   │   │   └── Layout.jsx              # App layout and navigation
│   │   ├── App.jsx          # Main application with routing
│   │   └── App.css          # PolyU-themed styling
│   ├── Dockerfile           # Frontend container configuration
│   └── package.json         # Node.js dependencies
│
├── desktop/                 # Electron desktop wrapper
│   ├── main.js              # Electron main process
│   └── package.json         # Electron dependencies
│
├── assets/                  # Application icons
│   ├── icon.png             # PNG icon
│   └── icon.icns            # macOS icon
│
├── docker-compose.yml       # Multi-container orchestration
├── run.sh                   # macOS/Linux startup script
├── run.ps1                  # Windows PowerShell startup script
├── ERD.png                  # Entity-Relationship Diagram
└── PROJECT_REPORT.md        # Project report documentation
```

## Database Schema

The system uses a normalized relational database with the following entities:

- **Person**: Personal information with hierarchical supervisor relationships
- **Profile**: One-to-one relationship with Person for job roles and status
- **School**: Academic units with department and faculty information
- **Location**: Physical locations linked to buildings and schools
- **Activity**: Events and activities organized by people at specific locations
- **Maintenance**: Maintenance tasks with type, frequency, and chemical usage tracking
- **ExternalCompany**: Contracted companies for maintenance services
- **Participation**: Many-to-many relationship between Person and Activity
- **Affiliation**: Many-to-many relationship between Person and School

## API Endpoints

The backend provides RESTful API endpoints for:

### Entity CRUD Operations

- `/api/persons` - Person management (GET, POST, PUT, DELETE)
- `/api/profiles` - Profile management
- `/api/schools` - School/Department management
- `/api/locations` - Location management (buildings, floors, rooms)
- `/api/activities` - Activity management
- `/api/maintenance` - Maintenance task management
- `/api/companies` - External company management

### Relationship Management

- `/api/participations` - Person-Activity relationships
- `/api/affiliations` - Person-School relationships

### Special Operations

- `/api/search/safety` - Safety search for chemical hazards by building
- `/api/query` - Execute SQL queries (Dev Console)
- `/api/import` - Bulk import from CSV data

### Dashboard Statistics

- `/api/maintenance-summary` - Maintenance tasks by type
- `/api/people-summary` - People distribution by role
- `/api/activities-summary` - Activities by type
- `/api/school-stats` - School statistics

## Development Notes

### Backend (Flask)

- Runs on port **5050** (not 5000)
- Automatic database initialization on first startup
- Seed data generation available via `backend/seed_data.py`
- CORS enabled for frontend communication
- Full SQL query support with dangerous operation warnings on frontend

### Frontend (React + Vite)

- Runs on port **5173**
- API URL configured to `http://localhost:5050/api`
- Uses Recharts for data visualization
- localStorage persistence for Dev Console query history
- Responsive design with PolyU branding
- CSV import/export functionality for all tables

### Docker Setup

- MySQL 8.0 database on internal network
- Backend waits for database readiness before starting
- Frontend depends on backend availability
- Persistent volume for database data
- All services restart automatically unless stopped

### Electron App

- Wraps the web application in a desktop window
- No external browser required
- Checks for Docker and Node.js installation
- Waits for frontend readiness before loading
- Provides native desktop experience

## Current Status

✅ **Completed Features:**

- Full database schema with normalized relationships (9 tables)
- Complete REST API with CRUD operations for all entities
- Executive dashboard with real-time visualizations
- Entity management interfaces (People, Schools, Locations, Activities, Maintenance)
- Relationship management (Participations, Affiliations)
- Safety search functionality for chemical hazards
- Dev Console with full SQL support and safety warnings
- CSV bulk import and export functionality
- Docker containerization with MySQL, Flask, React
- Electron desktop wrapper
- Automated startup scripts (run.sh, run.ps1)
- Mock data generation with seed_data.py
- PolyU-themed UI with responsive design

🚧 **Known Limitations:**

- No user authentication/authorization system
- Limited error handling in some edge cases

## Troubleshooting

### Docker Issues

- Ensure Docker Desktop is running before executing `run.sh` or `run.ps1`
- Check Docker daemon status: `docker info`
- View container logs: `docker compose logs -f`
- Restart containers: `docker compose restart`

### Database Connection Issues

- Verify MySQL container is running: `docker compose ps`
- Check backend logs for connection errors
- Ensure `.env` file has correct credentials (manual setup only)

### Frontend Not Loading

- Check if backend is accessible: `curl http://localhost:5050/api/persons`
- Verify frontend container is running
- Check browser console for errors
- Ensure API_URL in `frontend/src/App.jsx` matches backend port

### Port Conflicts

- Backend uses port 5050 (change in `docker-compose.yml` if needed)
- Frontend uses port 5173 (change in `docker-compose.yml` if needed)
- MySQL uses internal Docker network (not exposed to host)

## License

This project is developed for educational purposes as part of COMP2411 Database System course at The Hong Kong Polytechnic University.
