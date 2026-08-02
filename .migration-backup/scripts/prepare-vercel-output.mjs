import fs from "node:fs";
import path from "node:path";

const cwd = process.cwd();
const outputDirectory = path.resolve(cwd, "dist");
const candidates = [
  path.resolve(cwd, "artifacts/admin-panel/dist"),
  outputDirectory,
];

const sourceDirectory = candidates.find((directory) =>
  fs.existsSync(path.join(directory, "index.html")),
);

if (!sourceDirectory) {
  throw new Error(
    `Vercel build output not found. Checked: ${candidates.join(", ")}`,
  );
}

if (path.resolve(sourceDirectory) !== outputDirectory) {
  fs.rmSync(outputDirectory, { recursive: true, force: true });
  fs.cpSync(sourceDirectory, outputDirectory, { recursive: true });
}

const indexFile = path.join(outputDirectory, "index.html");
if (!fs.existsSync(indexFile)) {
  throw new Error(`Vercel output is missing ${indexFile}`);
}

console.log(`Vercel output prepared at ${outputDirectory}.`);