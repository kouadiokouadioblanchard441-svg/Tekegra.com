---
name: Prediction cooldown
description: Shared throttling rules for Telegram prediction generation
---

All prediction-generating actions share one per-user 121-second cooldown across Lucky Jet, Mines, and Rocket Queen. The slot is reserved before awaited work so rapid duplicate callbacks cannot generate two predictions. Access checks that reject a request must release the reservation.

**Why:** Users can tap another prediction button while the first callback is still processing, and a game-specific or free-only check is not sufficient to prevent simultaneous predictions.

**How to apply:** Any new prediction handler must reserve the shared slot before generation, release it when quota/access validation fails, and record the signal after successful generation. Menu navigation that does not generate a prediction must not reserve the slot.