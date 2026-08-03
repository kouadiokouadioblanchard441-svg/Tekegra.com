import { build } from "esbuild";
import { rm } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(fileURLToPath(import.meta.url));
const dist = path.join(root, "dist");
await rm(dist, { recursive: true, force: true });

await build({
  entryPoints: {
    index: path.join(root, "index.ts"),
    migrate: path.join(root, "scripts/migrate.ts"),
  },
  bundle: true,
  platform: "node",
  format: "esm",
  outdir: dist,
  sourcemap: false,
  packages: "bundle",
  logLevel: "info",
  banner: {
    js: "import { createRequire } from 'node:module'; globalThis.require = createRequire(import.meta.url);",
  },
});