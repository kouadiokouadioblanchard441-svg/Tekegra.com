---
name: Admin panel build fixes
description: Two import errors that blocked the Vite production build of artifacts/admin-panel
---

**Fix 1 — Missing generated API client:**
Pages imported `@/lib/api-client-react/src/generated/api` but no such local path existed.
The real files are in the workspace lib `lib/api-client-react/src/generated/`.
Solution: created a re-export bridge at `artifacts/admin-panel/src/lib/api-client-react/src/generated/api.ts`:
```ts
export * from "@workspace/api-client-react";
```

**Fix 2 — Wrong relative import in Sidebar:**
`artifacts/admin-panel/src/components/layout/Sidebar.tsx` imported `"./ui/button"` but
the button component is one level up at `../ui/button`.

**Why:** These were likely created by an agent that didn't test the production build.

**How to apply:** If the admin panel build fails with similar ENOENT errors, check for both deep-path workspace imports and relative path mistakes in components.
