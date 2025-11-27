# CMMS Project

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

- `backend/`: Flask application and database logic.
- `frontend/`: React application with Vite.
