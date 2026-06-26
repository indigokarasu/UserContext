# Mood Inference Reference

Mood is inferred from session patterns. Read recent sessions via `session_search`:

| Signal | Inference |
|--------|-----------|
| Short, clipped responses, minimal engagement | focused / busy |
| Long questions, exploratory language | curious / generative |
| Corrections, frustration words, "again" | frustrated |
| Multiple rapid requests, urgency markers | energized / stressed |
| Humor, tangents, casual tone | relaxed / playful |
| Silence (no sessions for 2+ days) | unknown |

**Default:** If no recent session activity, mood = "unknown"
**Confidence:** Never state confidence. Pick the best fit. If ambiguous between two, pick the more neutral one. Never output "mixed" or list multiple moods. One word only.
