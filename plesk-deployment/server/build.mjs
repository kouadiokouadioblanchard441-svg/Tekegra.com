import { build } from "esbuild";
import { rm } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(fileURLToPath(import.meta.url));
const dist = path.resolve(root, "..", "dist");
await rm(dist, { recursive: true, force: true });

await build({
  entryPoints: [path.join(root, "index.ts")],
  bundle: true,
  platform: "node",
  format: "cjs",
  outfile: path.join(dist, "index.cjs"),
  sourcemap: false,
  packages: "bundle",
  logLevel: "info",
});