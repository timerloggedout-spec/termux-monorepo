---
name: gtfs
description: Validate a GTFS Schedule feed (a GTFS ZIP file, a local path, or a public feed URL) with the GTFS Analyzer engine and explain publishability, scores, and the highest-priority fixes. Use when the user asks to validate, check, or analyze a GTFS feed or transit timetable ZIP, asks what a GTFS rule ID means, or types /gtfs.
---

# GTFS Validator

Validate the feed with the GTFS Analyzer engine and explain its result. The engine is the
only source of findings: never invent notices, recompute scores, or override its verdict.
Never send the feed anywhere; the analysis runs locally.

## 1. Get the feed

- **An attached ZIP or a local path**: use that file.
- **A public URL**: download it once to a local file, for example
  `curl -fL --max-time 120 -o feed.zip "<url>"`. In the chat's code sandbox, outbound requests
  to most sites are blocked (the download fails with a proxy error or HTTP 403). If the download
  fails for that reason, do not look for a workaround: ask the user to download the ZIP and
  attach it to the conversation.
- **Nothing given**: ask for a GTFS ZIP, or a public feed URL when running on the user's computer.

## 2. Make sure the engine is installed

Run `python3 -c "import gtfs_analyzer; print(gtfs_analyzer.__version__)"`. If that fails or
prints a version other than 0.19.0, install the pinned version:

```
pip install gtfs-analyzer==0.19.0
```

If pip refuses with "externally-managed-environment": in the chat's code sandbox, add
`--break-system-packages`; on the user's own computer, create a virtual environment instead
(`python3 -m venv ~/.cache/gtfs-validator/venv`) and use its `python` for the install and the
analysis. Never install into the user's system Python with `--break-system-packages`.

Ready-made packages exist for Linux x86_64, macOS on Apple silicon, and Windows x86_64. On other
platforms, such as an Intel Mac or Linux on ARM, pip falls back to building from source, which
needs a Rust toolchain. Do not attempt that build. Tell the user and point them to the browser
version at https://ttezer.github.io/gtfs-analyzer/, which runs the same engine on their device.
Do the same if PyPI cannot be reached.

## 3. Run the analysis

```
python3 ${CLAUDE_SKILL_DIR}/scripts/analyze.py <feed.zip> --lang <en|tr|fr|ja>
```

If `${CLAUDE_SKILL_DIR}` is not replaced, use `scripts/analyze.py` relative to this file.

**Language**: pass the user's language when it is English, Turkish, French, or Japanese. For any
other language pass `en`, then write your explanation in the user's language; keep rule IDs as
they are.

The script prints one JSON object; read it, not the raw engine output. Time and memory grow
with the number of findings, not the file size: a feed with 200,000 findings takes seconds, but
one with 900,000 findings took about 70 seconds and 5.5 GB of memory in the chat's code
sandbox. The summary stays small either way. If the run is killed for lack of memory, say so
and point the user to the browser version.

| Exit code | `error` | Meaning and what to do |
|---|---|---|
| 0 | — | Summary printed. Explain it (step 4). |
| 2 | `FATAL` | The engine could not open or read the feed, for example a corrupt ZIP. Report it as an analysis failure, not as a verdict on the feed, and quote `message`. |
| 3 | `PACKAGE_MISSING` | Go back to step 2. |
| 4 | `INPUT` | Bad argument or unreadable path. Fix the call and run again. |

## 4. Explain the result

Report, in this order:

1. **Publishability**: `publishability.publishable` as returned. If it is false, list the
   `blockers`. Do not call a feed unpublishable because of other notices, and do not call it
   publishable when the engine says it is not.
2. **Scores**: `scores` (overall, pub, spec, interop, quality, analytics) exactly as returned.
3. **Feed at a glance**: stop, route, and trip counts and the service window from `metrics`.
4. **What to fix first**: `r9_priorities` in the given order. For each, give the rule ID, title,
   how many instances, the remediation, and one concrete example (file, line, values). Keep the
   engine's order: do not reorder, merge, or skip priorities above the ones you list. You may
   note that two rules share a cause, after listing both.
5. **Totals**: `severity_counts` and `total_notices`. ANALYTICS and QUALITY findings describe the
   feed; they do not make it invalid by themselves.

If `validation_status` is `PARTIAL`, say first that coverage is incomplete, list
`partial.unavailable_files`, and explain that checks depending on them did not run. If
`version_warning` is present, mention which engine version produced the result.

Keep it short: a table for the scores, one or two lines per priority, and the remaining
priorities summarized in a sentence. Offer to run the analysis again on a corrected file.

### Example

> **Publishable: yes.** No blocking issues. One critical timing error should still be fixed.
>
> | Overall | Pub | Spec | Interop | Quality | Analytics |
> |---|---|---|---|---|---|
> | 95.9 | 100.0 | 100.0 | 92.6 | 92.6 | 96.2 |
>
> 4 stops, 1 route, 2 trips; service 2026-10-01 to 2026-12-31.
>
> **Fix first**
> 1. **STM_008**: stop times go backwards (critical, 1 instance). `stop_times.txt` line 4, trip
>    T1: arrival at S3 is 08:05:00, after 08:10:00 at S2. Times must increase along a trip.
> 2. **STP_022**: `stop_code` is missing for all 4 stops (medium). Add short codes riders know.
>
> 23 findings in total: 1 critical, 1 high, 3 medium, 2 low, 16 info.

## Rule questions

When the user asks what a rule ID means (for example `/gtfs TRP_002`):

1. If a result you already have contains the rule, answer from its `title`, `remediation`, and
   examples.
2. Otherwise look the rule up in the rule list for engine 0.19.0, in the user's language
   (`references/rules.<en|tr|fr|ja>.md`; `en` for other languages). Do not read the whole file;
   search for the row, matching the ID exactly:

   ```
   grep -F "| TRP_002 |" ${CLAUDE_SKILL_DIR}/references/rules.en.md
   ```

   The row gives the title, severity, and class. The `##` heading above it names the rule group.
   The list has no remediation text: explain what the title means for the feed and say that the
   exact fix and affected rows come from analyzing a feed.
3. If the ID is not in the list, say that the engine has no such rule. Do not guess one.
