/**
 * Builds artifacts/api-server/src/app.ts for use as a Vercel Node serverless
 * function.  Unlike build.mjs (which builds src/index.ts with app.listen()),
 * this target exports the Express app directly so Vercel can wrap it.
 *
 * Output: artifacts/api-server/dist-vercel/vercel-app.mjs  (+ pino workers)
 */
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";
import fs from "node:fs";
import { rm } from "node:fs/promises";
import { build as esbuild } from "esbuild";
import esbuildPluginPino from "esbuild-plugin-pino";

// esbuild-plugin-pino and some CJS packages need require() at module load time.
globalThis.require = createRequire(import.meta.url);

const artifactDir = path.dirname(fileURLToPath(import.meta.url));
const distVercel = path.resolve(artifactDir, "dist-vercel");

await rm(distVercel, { recursive: true, force: true });

await esbuild({
  entryPoints: [path.resolve(artifactDir, "src/app.ts")],
  platform: "node",
  bundle: true,
  format: "esm",
  // pino plugin injects extra worker entry points → must use outdir, not outfile
  outdir: distVercel,
  outExtension: { ".js": ".mjs" },
  logLevel: "info",
  external: [
    "*.node", "sharp", "bcrypt", "argon2", "fsevents", "re2", "farmhash",
    "bufferutil", "utf-8-validate", "pg-native", "better-sqlite3", "sqlite3",
    "canvas", "dtrace-provider",
  ],
  sourcemap: false,
  plugins: [esbuildPluginPino({ transports: ["pino-pretty"] })],
  banner: {
    js: `import { createRequire as __cr } from 'node:module';
import __p from 'node:path';
import __u from 'node:url';
globalThis.require = __cr(import.meta.url);
globalThis.__filename = __u.fileURLToPath(import.meta.url);
globalThis.__dirname = __p.dirname(globalThis.__filename);
`,
  },
});

// Rename app.mjs → vercel-app.mjs so the prepare script has a stable filename
const main = path.resolve(distVercel, "app.mjs");
const dest = path.resolve(distVercel, "vercel-app.mjs");
if (fs.existsSync(main)) {
  fs.renameSync(main, dest);
}

console.log("Vercel app bundle → dist-vercel/vercel-app.mjs");
