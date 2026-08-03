import { cp, mkdir, rm } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = path.resolve(packageRoot, "..");

const copies = [
  ["dist/index.cjs", path.join(repositoryRoot, "dist", "index.cjs")],
  ["client-dist", path.join(repositoryRoot, "client-dist")],
];

for (const [relativeSource, destination] of copies) {
  const source = path.join(packageRoot, relativeSource);
  await mkdir(path.dirname(destination), { recursive: true });
  await rm(destination, { recursive: true, force: true });
  await cp(source, destination, { recursive: true });
}

console.log("Root Plesk deployment files synchronized.");