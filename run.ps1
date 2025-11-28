# Kill existing processes (best effort)
Get-Process -Name python, node -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*PolyU CMMS*" } | Stop-Process -Force

Write-Host "🚀 Starting PolyU CMMS..." -ForegroundColor Cyan

# 0. Start MySQL
Write-Host "🗄️  Starting MySQL..." -ForegroundColor Green
try {
    Start-Service -Name "MySQL" -ErrorAction Stop
    Write-Host "✅ MySQL Service started." -ForegroundColor Green
} catch {
    Write-Warning "Could not start MySQL service automatically. It might not be installed as a service or requires Admin privileges."
    Write-Warning "Please ensure MySQL is running manually."
}

# 1. Start Backend
Write-Host "📦 Launching Backend (Port 5050)..." -ForegroundColor Green
Set-Location backend
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv venv
}
# Activate venv in a way that persists for the command
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt | Out-Null
Start-Process -FilePath "python" -ArgumentList "app.py" -NoNewWindow
Set-Location ..

# 2. Start Frontend
Write-Host "💻 Launching Frontend..." -ForegroundColor Green
Set-Location frontend
npm install | Out-Null
Start-Process -FilePath "npm.cmd" -ArgumentList "run dev" -NoNewWindow
Set-Location ..

# 3. Start Desktop
Write-Host "🖥️  Launching Desktop App..." -ForegroundColor Green
Set-Location desktop
npm install | Out-Null
npm start
Set-Location ..