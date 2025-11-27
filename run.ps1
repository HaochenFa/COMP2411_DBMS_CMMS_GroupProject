Param(
    [string]$AppUrl = "http://localhost:5173"
)

Write-Host "[run.ps1] Starting CMMS stack using Docker Compose..." -ForegroundColor Cyan

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "[run.ps1] Docker is not installed or not on PATH. Please install Docker Desktop from https://www.docker.com/products/docker-desktop." \
        -ErrorAction Stop
}

$useDockerComposeExe = $false
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    $useDockerComposeExe = $true
}

try {
    if ($useDockerComposeExe) {
        Write-Host "[run.ps1] Running: docker-compose up -d --build" -ForegroundColor Cyan
        docker-compose up -d --build
    }
    else {
        Write-Host "[run.ps1] Running: docker compose up -d --build" -ForegroundColor Cyan
        docker compose up -d --build
    }
}
catch {
    Write-Error "[run.ps1] Failed to start Docker containers: $_"
    exit 1
}

Write-Host "[run.ps1] Waiting for frontend to become available at $AppUrl ..." -ForegroundColor Cyan

$maxAttempts = 30
$ready = $false

for ($i = 1; $i -le $maxAttempts; $i++) {
    try {
        $response = Invoke-WebRequest -Uri $AppUrl -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
            $ready = $true
            break
        }
    }
    catch {
        # Ignore and retry
    }
    Start-Sleep -Seconds 2
}

if ($ready) {
    Write-Host "[run.ps1] Frontend appears to be up." -ForegroundColor Green
}
else {
    Write-Warning "[run.ps1] Frontend did not become ready within the expected time, but containers are running."
}

Write-Host "[run.ps1] Opening browser at $AppUrl ..." -ForegroundColor Cyan
Start-Process $AppUrl
