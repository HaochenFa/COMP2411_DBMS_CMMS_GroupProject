# CMMS Project

## Prerequisites

- Python 3.8+
- Node.js 16+
- MySQL Server

## Setup & Running

### 1. Database Setup

Ensure your MySQL server is running. Create a database (default name `cmms_db`) or let the initialization script do it.

### 2. Backend (Flask)

1. Navigate to the project root.
2. Create a virtual environment (optional but recommended):

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r backend/requirements.txt
    ```

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
