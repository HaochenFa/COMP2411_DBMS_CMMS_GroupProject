// Electron main process for CMMS desktop wrapper
// - Starts the Docker-based stack (db, backend, frontend)
// - Waits for the frontend to be ready
// - Loads the app into a BrowserWindow (no external browser needed)

const { app, BrowserWindow, dialog } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const http = require("http");

const FRONTEND_URL = process.env.FRONTEND_URL || "http://localhost:5173";
const MAX_RETRIES = 60;
const RETRY_DELAY_MS = 2000;

function runCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      stdio: "inherit",
      shell: false,
      ...options,
    });

    child.on("error", (err) => reject(err));
    child.on("exit", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`${command} ${args.join(" ")} exited with code ${code}`));
      }
    });
  });
}

async function startDockerStack() {
  const projectRoot = path.join(__dirname, "..");

  // Prefer modern `docker compose`, fall back to legacy `docker-compose`.
  const candidates = [
    { cmd: "docker", args: ["compose", "up", "-d", "--build"] },
    { cmd: "docker-compose", args: ["up", "-d", "--build"] },
  ];

  let lastError = null;
  for (const candidate of candidates) {
    try {
      await runCommand(candidate.cmd, candidate.args, { cwd: projectRoot });
      return;
    } catch (err) {
      lastError = err;
    }
  }

  throw lastError || new Error("Failed to start Docker stack");
}

function waitForFrontendReady(url, maxRetries = MAX_RETRIES, delayMs = RETRY_DELAY_MS) {
  const target = new URL(url);

  return new Promise((resolve, reject) => {
    let attempts = 0;

    const attempt = () => {
      attempts += 1;

      const req = http.get(
        {
          hostname: target.hostname,
          port: target.port,
          path: target.pathname,
          timeout: 2000,
        },
        (res) => {
          // Consider any non-5xx response as "service is up".
          if (res.statusCode && res.statusCode < 500) {
            res.resume();
            resolve();
          } else if (attempts >= maxRetries) {
            res.resume();
            reject(new Error(`Frontend not ready after ${attempts} attempts`));
          } else {
            res.resume();
            setTimeout(attempt, delayMs);
          }
        }
      );

      req.on("error", () => {
        if (attempts >= maxRetries) {
          reject(new Error(`Frontend not reachable after ${attempts} attempts`));
        } else {
          setTimeout(attempt, delayMs);
        }
      });
    };

    attempt();
  });
}

async function createMainWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  try {
    // await startDockerStack(); // Removed Docker dependency
    console.log("Waiting for frontend to be ready...");
    await waitForFrontendReady(FRONTEND_URL);
    await win.loadURL(FRONTEND_URL);
  } catch (err) {
    console.error("Failed to start app stack:", err);
    dialog.showErrorBox(
      "Startup error",
      `Failed to connect to the application.\n\n${err && err.message ? err.message : String(err)}`
    );
  }
}

app.whenReady().then(() => {
  createMainWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
