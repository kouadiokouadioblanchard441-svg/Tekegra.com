---
name: Vercel workspace output
description: Vercel may run a monorepo build from a configured artifact directory rather than repository root.
---

Vercel's current working directory can differ from the repository root when a
Root Directory is configured. Deployment scripts must resolve output relative to
the actual working directory and verify the final index file before completion.

**Why:** Assuming `artifacts/admin-panel/dist` from every working directory caused
successful frontend builds to fail during the final output-copy step.

**How to apply:** Use a small Node preparation script that checks both the
artifact-relative output and the current `dist`, then copies/verifies the final
output directory declared to Vercel.