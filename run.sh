#!/bin/bash

# Kill any running processes on ports 5050 (backend) and 5173 (frontend)
lsof -ti:5050 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

echo "🚀 Starting PolyU CMMS..."

# 0. Start MySQL
echo "🗄️  Starting MySQL..."
if command -v brew >/dev/null 2>&1; then
	brew services start mysql || echo "MySQL might already be running or failed to start via brew."
elif command -v mysql.server >/dev/null 2>&1; then
	mysql.server start || echo "MySQL might already be running."
else
	echo "⚠️  Could not find a way to auto-start MySQL. Please ensure it is running."
fi

# Wait for MySQL to be ready
echo "⏳ Waiting for MySQL to be ready..."
MAX_RETRIES=30
COUNT=0
while ! mysqladmin ping -h "localhost" --silent; do
	sleep 1
	COUNT=$((COUNT + 1))
	if [ $COUNT -ge $MAX_RETRIES ]; then
		echo "❌ MySQL failed to start or is not reachable."
		exit 1
	fi
	echo -n "."
done
echo "✅ MySQL is up!"

# 1. Start Backend
echo "📦 Launching Backend (Port 5050)..."
cd backend
if [ ! -d "venv" ]; then
	echo "Creating Python virtual environment..."
	python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt >/dev/null 2>&1
python3 app.py &
BACKEND_PID=$!
cd ..

# 2. Start Frontend
echo "💻 Launching Frontend..."
cd frontend
npm install >/dev/null 2>&1
npm run dev &
FRONTEND_PID=$!
cd ..

# 3. Start Desktop App (Electron)
echo "🖥️  Launching Desktop App..."
cd desktop
npm install >/dev/null 2>&1
npm start &
DESKTOP_PID=$!
cd ..

echo "✅ System is running!"
echo "   - Backend: http://127.0.0.1:5050"
echo "   - Frontend: http://localhost:5173"
echo "   - Desktop App: Launched"
echo "   (Press CTRL+C to stop)"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID $DESKTOP_PID
