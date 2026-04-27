import { build } from "esbuild";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { basename, resolve } from "node:path";

const root = process.cwd();
const distDir = resolve(root, "dist");
const assetsDir = resolve(distDir, "assets");

await mkdir(assetsDir, { recursive: true });

const apiUrl = process.env.VITE_API_URL ?? "http://127.0.0.1:8000/api/v1";

const result = await build({
  entryPoints: [resolve(root, "src/main.tsx")],
  bundle: true,
  outdir: assetsDir,
  entryNames: "index",
  format: "esm",
  platform: "browser",
  target: ["es2020"],
  minify: true,
  sourcemap: false,
  loader: {
    ".css": "css",
  },
  define: {
    "import.meta.env.VITE_API_URL": JSON.stringify(apiUrl),
  },
  metafile: true,
  logLevel: "info",
});

const cssFiles = Object.keys(result.metafile.outputs).filter((file) => file.endsWith(".css"));
const cssLink = cssFiles.map((file) => `<link rel="stylesheet" href="/assets/${basename(file)}">`).join("\n    ");

const html = await readFile(resolve(root, "index.html"), "utf8");
const outputHtml = html
  .replace('<script type="module" src="/src/main.tsx"></script>', '<script type="module" src="/assets/index.js"></script>')
  .replace("</head>", `${cssLink ? `    ${cssLink}\n` : ""}</head>`);

await writeFile(resolve(distDir, "index.html"), outputHtml, "utf8");
