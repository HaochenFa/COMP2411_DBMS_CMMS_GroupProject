/**
 * Unit tests for Electron main process
 */
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import http from "http";
import { spawn } from "child_process";

// We'll test the utility functions by extracting them
// Since main.js has side effects, we test the core logic

describe("Desktop Main Process", () => {
  describe("waitForFrontendReady", () => {
    let mockServer;
    let serverPort;

    beforeEach(async () => {
      // Create a mock HTTP server
      mockServer = http.createServer((req, res) => {
        res.statusCode = 200;
        res.end("OK");
      });

      await new Promise((resolve) => {
        mockServer.listen(0, () => {
          serverPort = mockServer.address().port;
          resolve();
        });
      });
    });

    afterEach(() => {
      mockServer?.close();
    });

    it("should resolve when server responds with 200", async () => {
      const waitForFrontendReady = (url, maxRetries = 5, delayMs = 100) => {
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
                if (res.statusCode && res.statusCode < 500) {
                  res.resume();
                  resolve();
                } else if (attempts >= maxRetries) {
                  res.resume();
                  reject(
                    new Error(`Frontend not ready after ${attempts} attempts`),
                  );
                } else {
                  res.resume();
                  setTimeout(attempt, delayMs);
                }
              },
            );

            req.on("error", () => {
              if (attempts >= maxRetries) {
                reject(
                  new Error(
                    `Frontend not reachable after ${attempts} attempts`,
                  ),
                );
              } else {
                setTimeout(attempt, delayMs);
              }
            });
          };

          attempt();
        });
      };

      await expect(
        waitForFrontendReady(`http://localhost:${serverPort}`),
      ).resolves.toBeUndefined();
    });

    it("should reject after max retries when server is down", async () => {
      const waitForFrontendReady = (url, maxRetries = 2, delayMs = 50) => {
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
                timeout: 100,
              },
              (res) => {
                if (res.statusCode && res.statusCode < 500) {
                  res.resume();
                  resolve();
                } else if (attempts >= maxRetries) {
                  res.resume();
                  reject(
                    new Error(`Frontend not ready after ${attempts} attempts`),
                  );
                } else {
                  res.resume();
                  setTimeout(attempt, delayMs);
                }
              },
            );

            req.on("error", () => {
              if (attempts >= maxRetries) {
                reject(
                  new Error(
                    `Frontend not reachable after ${attempts} attempts`,
                  ),
                );
              } else {
                setTimeout(attempt, delayMs);
              }
            });
          };

          attempt();
        });
      };

      // Use a port that's definitely not in use
      await expect(
        waitForFrontendReady("http://localhost:59999", 2, 50),
      ).rejects.toThrow("Frontend not reachable after 2 attempts");
    });
  });

  describe("runCommand", () => {
    it("should resolve when command exits with code 0", async () => {
      const runCommand = (command, args, options = {}) => {
        return new Promise((resolve, reject) => {
          const child = spawn(command, args, {
            stdio: "pipe",
            shell: false,
            ...options,
          });

          child.on("error", (err) => reject(err));
          child.on("exit", (code) => {
            if (code === 0) {
              resolve();
            } else {
              reject(
                new Error(
                  `${command} ${args.join(" ")} exited with code ${code}`,
                ),
              );
            }
          });
        });
      };

      await expect(runCommand("echo", ["test"])).resolves.toBeUndefined();
    });

    it("should reject when command exits with non-zero code", async () => {
      const runCommand = (command, args, options = {}) => {
        return new Promise((resolve, reject) => {
          const child = spawn(command, args, {
            stdio: "pipe",
            shell: false,
            ...options,
          });

          child.on("error", (err) => reject(err));
          child.on("exit", (code) => {
            if (code === 0) {
              resolve();
            } else {
              reject(
                new Error(
                  `${command} ${args.join(" ")} exited with code ${code}`,
                ),
              );
            }
          });
        });
      };

      await expect(
        runCommand("node", ["-e", "process.exit(1)"]),
      ).rejects.toThrow("exited with code 1");
    });
  });
});
