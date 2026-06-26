# Constraints and Design Decisions

## Hard constraints

- **300 words max.** If over, compress further. Cut bullets before snapshot.
- **No fabrication.** If calendar is empty, say so ("No scheduled events"). If no session data, mood = "unknown".
- **No weather.** Vesper handles weather. This is purely personal context.
- **No advice or suggestions.** This is a snapshot, not a recommendation.
- **No markdown tables.** Telegram doesn't render them. Use bullet lists or inline text.
- **No em dashes.** Use commas or periods.
- **No meta-narration.** Just the data.
- **Never touch any other section of USER.md.** Only replace the `## Daily Context` block.

## Design decisions

- **Single file output:** The skill writes to one section of one file. Splitting to reference files would add indirection without reducing context cost at 157 lines.
- **Mood over facts:** Mood is inferred, not asked. The inference table is deliberately simple (6 signals) to avoid over-reading. If wrong, tomorrow's run corrects it.
- **Three-day window:** Yesterday/today/tomorrow is the useful working memory window. Beyond that, Vesper handles.
