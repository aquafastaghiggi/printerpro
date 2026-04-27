import { spawn, spawnSync } from "node:child_process";
import { resolve } from "node:path";

const root = process.cwd();
const backendPort = Number(process.env.BACKEND_PORT ?? 8000);
const frontendPort = Number(process.env.PORT ?? 4173);
const backendUrl = `http://127.0.0.1:${backendPort}`;
const frontendUrl = `http://127.0.0.1:${frontendPort}`;

function run(command, args, options = {}) {
  const child = spawn(command, args, {
    cwd: root,
    stdio: "inherit",
    shell: process.platform === "win32",
    ...options,
  });
  return child;
}

const build = spawnSync("node", ["scripts/build-web.mjs"], {
  cwd: root,
  stdio: "inherit",
  shell: process.platform === "win32",
});

if (build.status !== 0) {
  process.exit(build.status ?? 1);
}

const seed = spawnSync("python", ["scripts/create_admin.py"], {
  cwd: root,
  stdio: "inherit",
  shell: process.platform === "win32",
  env: {
    ...process.env,
    AUTO_CREATE_TABLES: "true",
  },
});

if (seed.status !== 0) {
  process.exit(seed.status ?? 1);
}

const backend = run("python", ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", String(backendPort)], {
  env: {
    ...process.env,
    AUTO_CREATE_TABLES: "true",
  },
});
const frontend = run("node", ["scripts/serve-web.mjs"], {
  env: {
    ...process.env,
    PORT: String(frontendPort),
  },
});

const shutdown = () => {
  backend.kill();
  frontend.kill();
};

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

console.log(`Backend: ${backendUrl}`);
console.log(`Frontend: ${frontendUrl}`);
console.log("Empresa modelo: Empresa Modelo | login: demo@printerpro.com | senha: 123456");
console.log("Abra o frontend para visualizar o sistema no localhost.");

backend.on("exit", (code) => {
  if (code && code !== 0) {
    frontend.kill();
    process.exit(code);
  }
});

frontend.on("exit", (code) => {
  if (code && code !== 0) {
    backend.kill();
    process.exit(code);
  }
});
