Write-Host "[run.ps1] Launching CMMS Electron desktop app..." -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$desktopDir = Join-Path $scriptDir "desktop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
	Write-Error "[run.ps1] Docker CLI (docker) is not installed or not on PATH. Please install Docker Desktop from https://docs.docker.com/desktop/." -ErrorAction Stop
}

docker info | Out-Null 2>$null
if ($LASTEXITCODE -ne 0) {
	Write-Error "[run.ps1] Docker seems to be installed but the Docker daemon is not running or is not accessible. Please start Docker Desktop (or your Docker service) and try again." -ErrorAction Stop
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
	Write-Error "[run.ps1] npm (Node.js) is not installed or not on PATH. Please install Node.js from https://nodejs.org/." -ErrorAction Stop
}

if (-not (Test-Path $desktopDir)) {
    Write-Error "[run.ps1] desktop directory not found at $desktopDir."
    exit 1
}

Set-Location $desktopDir

if (-not (Test-Path "node_modules")) {
    Write-Host "[run.ps1] Installing Electron app dependencies (first-run setup)..." -ForegroundColor Cyan
    npm install
}

Write-Host "[run.ps1] Starting Electron app (npm start)..." -ForegroundColor Cyan
npm start
