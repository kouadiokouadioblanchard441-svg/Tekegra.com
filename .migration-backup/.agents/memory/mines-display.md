---
name: Mines display
description: User-facing Mines prediction wording
---

The Mines prediction must always display the trap label as “PIÈGES : 3 mines”, regardless of the internally generated mine count.

**Why:** The user explicitly wants the displayed trap mention to stay fixed at three.

**How to apply:** Keep the fixed wording in the user-facing prediction and analysis formatters; do not infer this display value from the generated signal.