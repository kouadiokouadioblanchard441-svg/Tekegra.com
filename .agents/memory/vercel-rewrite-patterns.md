---
name: Vercel rewrite patterns
description: Vercel rejects negative-lookahead regular expressions in rewrite source patterns.
---

Vercel rewrite `source` patterns must use its supported path syntax; negative-lookahead
regular expressions such as `(?!...)` are rejected during deployment.

**Why:** The deployment validator rejects these patterns before the build starts, so
API exclusions must be expressed as explicit routes or supported path parameters.

**How to apply:** Keep webhook routes explicit, route only the known API prefixes to
the API function, and use a final catch-all only after API routes have been declared.