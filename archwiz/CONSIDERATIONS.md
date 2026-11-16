# ArchWiz Considerations – Running Design Log

## Naming Lexicon (from Grimoire Protocol)
- TasQue = ta'Done (task completion declaration)
- Spellbook = Library of system abilities (not the task queue)
- Scry = Inspection / verification
- Sentinel = Verification gate
- Ascend = Promotion
- Phylactery = Backup
- Grid = Master index
- Weave = Function index
- Echo = Metrics
- Chronicle = Provenance log
- Chaff = Bloat exclusions

## Task Status Lexicon
- Seed = pending
- Bloomed = done (TasQue)
- Withered = failed

## Open Design Questions
- Should dispatch_task.py enforce target_type (source vs output)?
- Critique Daemon: name? (Scry? Sentinel? Argus?)
- Lexicon Filter: dashboard [13] or standalone?
- Refactor Rune: search/replace using character substitution table

## fzf Integration (Shelved)
- Issue: fzf in browse_dirs() indexed 194,276 files — doesn't respect bloat_exclusions.lst.
- Fix needed: pipe directory list through bloat filter before fzf (e.g., `find ~ -type d | grep -vFf bloat_exclusions.lst | fzf`).
- Issue: fzf hides keyboard in Termux — requires `termux-fix-shebang` or fzf-tmux wrapper.
- Status: Shelved until bloat filter and keyboard fix are ready.

## Prompt Engineering Performance Phrases
Observed that certain command phrases produce consistently strong results from DeepSeek:
- "Make it so" — triggers authoritative, complete implementation
- "Build the future now" — triggers visionary, forward‑looking design
- "Show me what you got" — triggers comprehensive disclosure of capabilities
- "Continue" — triggers next logical step without over‑prompting
- "GB" / "LFGOOO" — triggers high‑energy, rapid‑fire implementation mode

Platform‑specific observations:
- Claude responds well to "Show me what you got"
- Gemini responds to "Build the future now" (possibly Grok as well)
- DeepSeek responds to "Make it so"

Status: Observed. Pending formal A/B testing via prompt engine rotation.

## Prompt Engineering — Case Sensitivity & Emoji Modifiers
- **Case sensitivity**: "Make it so" (title case) triggers authoritative implementation. "make it so" (lowercase) triggers casual continuation. "MAKE IT SO" (uppercase) triggers urgent, no‑explanation mode.
- **Emoji modifiers**: 
  - 🪄 (magic wand) before a request triggers creative/novel solutions
  - ⚡ (lightning) triggers speed‑optimized responses
  - 🛡️ (shield) triggers defensive/validation‑heavy responses
  - 🔱 (trident) triggers multi‑pronged/comprehensive responses
  - 💪🏽🧠 (muscle + brain) triggers implementation + analysis combo
- **Punctuation**: "LFGOOO" (no exclamation) = energetic. "LFGOOO!" = urgent energetic. "LFGOOO!!!" = emergency mode (may trigger shorter responses).
- **GB** (Get Busy) = maintain momentum, don't over‑explain.
- **Continue** = next logical step, minimal context repetition.
- **"Make it so" + code block** = implement exactly what's shown, no alternatives.
- **"Show me what you got" + concept** = comprehensive exploration of the concept.

Status: Observed patterns. Pending controlled A/B testing via prompt engine rotation module.

## Prompt Engineering — Additional Phrases
- "Make it Happen" — triggers determined, pragmatic implementation with visible progress markers.
- "4π¢hW1z making it happen!" — self‑referential ArchWiz invocation; triggers cockpit‑aware, multi‑tool orchestration.
- "LFGOOO" — triggers high‑energy, rapid‑fire implementation mode.
- "GB" — Get Busy; maintain momentum, minimal explanation.
- "Continue" — next logical step, minimal context repetition.

Status: Observed. Pending formal A/B testing via prompt engine rotation.

- **[2026-06-13 13:51]** | **Listener scribe tags** | Already built – `#TIL`, `#procedure`, `#consideration` auto‑logged |

- **[2026-06-13 13:53]** The shell will now understand `#TIL`, `#procedure`, `#consideration`, `#concept`, and `#branch` tags directly — logging them to the same files the listener watches. It also gains quick access to the Archivist, the Mirror, and the activity feed.

- **[2026-06-13 13:55]** The shell will now understand `#TIL`, `#procedure`, `#consideration`, `#concept`, and `#branch` tags directly — logging them to the same files the listener watches. It also gains quick access to the Archivist, the Mirror, and the activity feed.

- **[2026-06-13 13:55]** | **Listener scribe tags** | Already built – `#TIL`, `#procedure`, `#consideration` auto‑logged |

## [16] Live View / Execution Review Panel — Feature Set (Frozen)

| Command | Behavior |
|---------|----------|
| `/exec <n>` | Execute block N immediately |
| `/exec all` | Execute all pending blocks |
| `/skip <n>` | Skip block N, log to exception_notes.md if note provided |
| `/send` | Multi‑line message to the current session |
| `/history` | Show recent exceptions and executions |
| `/sync` | Force a cache refresh from DeepSeek |
| `/q` | Quit back to cockpit |

- Opens with a fresh sync every time.
- Only shows **assistant code blocks** not yet executed or skipped.
- Notes appended to `~/archwiz/exception_notes.md`.
- Session auto‑detected from the most recent cache file.
- This feature is **frozen** until a formal redesign is planned.
