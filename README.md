# CMMS Project

## Prerequisites

- Python 3.8+
- Conda (e.g. Miniconda/Anaconda or Mambaforge)
- (Optional) [uv](https://github.com/astral-sh/uv) for fast Python package & virtual env management
- Node.js 16+
- MySQL Server

## Setup & Running

### 1. Database Setup

Ensure your MySQL server is running. Create a database (default name `cmms_db`) or let the initialization script do it.

### 2. Backend (Flask)

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

5. Initialize the database:
    Run this from the **project root**:

    ```bash
    python backend/db.py
    ```

6. Run the server:
    Run this from the **backend** directory:

    ```bash
    cd backend
    python app.py
    ```

    The backend will start on `http://localhost:5000`.

### 3. Frontend (Vite + React)

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

## Project Structure

- `backend/`: Flask application and database logic.
- `frontend/`: React application with Vite.
