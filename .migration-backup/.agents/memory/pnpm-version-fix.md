---
name: pnpm version mismatch on Replit
description: Fix for pnpm self-install loop when project declares older pnpm in packageManager field
---

**Symptom:** `pnpm install` fails with repeated `pnpm add pnpm@9.15.9 --loglevel=error --allow-build=@pnpm/exe ...` errors.

**Cause:** `package.json` declares `"packageManager": "pnpm@9.15.9"` but Replit installs pnpm 10.x. pnpm 10 sees the mismatch and tries to self-install the declared version in a loop.

**Fix:** Add `manage-package-manager-versions=false` to `.npmrc`. This prevents pnpm from attempting to install itself.

**Why:** Replit's pnpm version is managed by Nix/the platform — you can't override it via corepack. Disabling version management lets pnpm 10 run the workspace as-is (it's backward-compatible with pnpm 9 workspace configs).

**How to apply:** Whenever you see this loop error in a project with `packageManager: pnpm@X.Y.Z` in package.json and the installed pnpm version doesn't match.
