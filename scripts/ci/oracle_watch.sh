#!/usr/bin/env bash
# oracle_watch.sh — the Oracle's watch-and-evaluate loop.
# Tooling for the Oracle Codespaces lane (Evaluator role per docs/ops/SKILLS-INVENTORY.md).
# Implements the adaptive-wait discipline (.agents/skills/adaptive-wait/SKILL.md)
# applied to judging another agent's PR rather than the author's own promote decision.
#
# Usage: ./oracle_watch.sh <pr-number> [--max-cycles N] [--interval SECONDS]

set -euo pipefail

# ---------- Parse Arguments ----------
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <pr-number> [--max-cycles N] [--interval SECONDS]" >&2
    exit 1
fi

PR_NUM="$1"
shift

MAX_CYCLES=20
INTERVAL=30

while [ "$#" -gt 0 ]; do
    case "$1" in
        --max-cycles)
            MAX_CYCLES="$2"
            shift 2
            ;;
        --interval)
            INTERVAL="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

# ---------- Check Dependencies ----------
for cmd in gh jq; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: required command '$cmd' not found in PATH." >&2
        exit 1
    fi
done

# ---------- State Variables ----------
PREV_CHECKS_JSON=""
STALL_COUNT=0
CYCLE=1

echo "========================================================================"
echo "🔮 ORACLE WATCH-AND-EVALUATE LOOP ACTIVE (PR #$PR_NUM)"
echo "========================================================================"

# ---------- 1. CAPTURE ----------
echo "[oracle:CAPTURE] Fetching initial PR metadata..."
PR_META=$(gh pr view "$PR_NUM" --json headRefOid,title,url,mergeable,commits 2>/dev/null || true)

if [ -z "$PR_META" ]; then
    echo "Error: Could not fetch metadata for PR #$PR_NUM. Check PR number or gh auth status." >&2
    exit 1
fi

HEAD_SHA=$(echo "$PR_META" | jq -r '.headRefOid')
PR_TITLE=$(echo "$PR_META" | jq -r '.title')
PR_URL=$(echo "$PR_META" | jq -r '.url')
INITIAL_MERGEABLE=$(echo "$PR_META" | jq -r '.mergeable')

echo "  PR Title: $PR_TITLE"
echo "  PR URL:   $PR_URL"
echo "  Head SHA: $HEAD_SHA"
echo "  Expected: all required checks green + mergeable"
echo "------------------------------------------------------------------------"

# ---------- 1b. Provenance Check (VALIDATE) ----------
echo "[oracle:provenance] Running lightweight trailer & commit verification..."
COMMITS_JSON=$(echo "$PR_META" | jq -c '.commits')
if [ -n "$COMMITS_JSON" ] && [ "$COMMITS_JSON" != "null" ]; then
    # Heuristic: check if any commit message body is too short or looks like boilerplate
    BAD_COMMITS=$(echo "$COMMITS_JSON" | jq -r '.[] | select((.messageBody | length) < 20) | .oid + " (" + .messageHeadline + ")"')
    if [ -n "$BAD_COMMITS" ]; then
        echo "  ⚠️  [oracle:provenance] Warning: The following commits have short/boilerplate bodies (< 20 chars):"
        echo "$BAD_COMMITS" | sed 's/^/    - /'
    else
        echo "  ✅ [oracle:provenance] Commit bodies and trailers look descriptive."
    fi
else
    echo "  ⚠️  [oracle:provenance] Warning: Could not retrieve commit history for provenance check."
fi
echo "------------------------------------------------------------------------"

# ---------- Main Loop ----------
while [ "$CYCLE" -le "$MAX_CYCLES" ]; do
    echo "--- Cycle $CYCLE/$MAX_CYCLES ($(date -u +%Y-%m-%dT%H:%M:%SZ)) ---"

    # ---------- 2. WAIT ----------
    if [ "$CYCLE" -gt 1 ]; then
        echo "[oracle:WAIT] Sleeping for ${INTERVAL}s..."
        sleep "$INTERVAL"
    fi

    # ---------- 3. WATCH / RE-FETCH ----------
    echo "[oracle:WATCH] Fetching check runs for SHA $HEAD_SHA..."
    # Fetch checks via gh pr checks
    CHECKS_JSON=$(gh pr checks "$PR_NUM" --json name,state,conclusion 2>/dev/null || true)
    
    if [ -z "$CHECKS_JSON" ] || [ "$CHECKS_JSON" == "[]" ] || [ "$CHECKS_JSON" == "null" ]; then
        # Fallback to commit status API if checks list is empty
        CHECKS_JSON=$(gh api "repos/:owner/:repo/commits/$HEAD_SHA/check-runs" --jq '.check_runs[] | {name: .name, state: .status, conclusion: .conclusion}' 2>/dev/null || true)
    fi

    # Re-fetch mergeability
    CURRENT_MERGEABLE=$(gh pr view "$PR_NUM" --json mergeable --jq '.mergeable' 2>/dev/null || "UNKNOWN")

    # ---------- 4. VALIDATE ----------
    echo "[oracle:VALIDATE] Cross-checking check-run conclusions..."
    TOTAL_CHECKS=0
    SUCCESS_CHECKS=0
    FAILED_CHECKS=0
    IN_PROGRESS_CHECKS=0

    if [ -n "$CHECKS_JSON" ] && [ "$CHECKS_JSON" != "[]" ]; then
        # Parse checks
        while read -r check; do
            if [ -z "$check" ]; then continue; fi
            TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
            NAME=$(echo "$check" | jq -r '.name')
            STATE=$(echo "$check" | jq -r '.state')
            CONCLUSION=$(echo "$check" | jq -r '.conclusion')

            echo "  - $NAME: state=$STATE, conclusion=$CONCLUSION"

            if [ "$CONCLUSION" == "success" ]; then
                SUCCESS_CHECKS=$((SUCCESS_CHECKS + 1))
            elif [ "$CONCLUSION" == "failure" ] || [ "$CONCLUSION" == "cancelled" ] || [ "$CONCLUSION" == "timed_out" ] || [ "$CONCLUSION" == "action_required" ]; then
                FAILED_CHECKS=$((FAILED_CHECKS + 1))
            else
                IN_PROGRESS_CHECKS=$((IN_PROGRESS_CHECKS + 1))
            fi
        done <<< "$(echo "$CHECKS_JSON" | jq -c '.[]')"
    else
        echo "  ⚠️  No check runs reported yet."
    fi

    echo "  Summary: Total=$TOTAL_CHECKS, Success=$SUCCESS_CHECKS, Failed=$FAILED_CHECKS, In-Progress=$IN_PROGRESS_CHECKS, Mergeable=$CURRENT_MERGEABLE"

    # ---------- 5. COMPARE ----------
    if [ -n "$PREV_CHECKS_JSON" ]; then
        # Compare current checks JSON with previous to detect stalls
        if [ "$CHECKS_JSON" == "$PREV_CHECKS_JSON" ] && [ "$IN_PROGRESS_CHECKS" -gt 0 ]; then
            STALL_COUNT=$((STALL_COUNT + 1))
            echo "[oracle:COMPARE] No progress detected across consecutive cycles (Stall Count: $STALL_COUNT/3)"
        else
            STALL_COUNT=0
        fi
    fi
    PREV_CHECKS_JSON="$CHECKS_JSON"

    # ---------- 6. CLASSIFY ----------
    CLASSIFICATION="UNKNOWN"
    if [ "$FAILED_CHECKS" -gt 0 ]; then
        CLASSIFICATION="FAIL"
    elif [ "$STALL_COUNT" -ge 3 ]; then
        CLASSIFICATION="STALLED"
    elif [ "$TOTAL_CHECKS" -gt 0 ] && [ "$SUCCESS_CHECKS" -eq "$TOTAL_CHECKS" ] && [ "$CURRENT_MERGEABLE" == "MERGEABLE" ]; then
        CLASSIFICATION="PASS"
    elif [ "$TOTAL_CHECKS" -gt 0 ] && [ "$IN_PROGRESS_CHECKS" -gt 0 ]; then
        CLASSIFICATION="IN_PROGRESS"
    fi

    # ---------- 7. RECORD ----------
    echo "[oracle:RECORD] Cycle $CYCLE: CLASSIFICATION=$CLASSIFICATION, SHA=$HEAD_SHA, Mergeable=$CURRENT_MERGEABLE"
    echo "------------------------------------------------------------------------"

    # ---------- Loop Termination ----------
    if [ "$CLASSIFICATION" == "PASS" ]; then
        echo "========================================================================"
        echo "🔮 Oracle verdict: PASS"
        echo "All $TOTAL_CHECKS checks are green and PR is mergeable."
        echo "========================================================================"
        exit 0
    elif [ "$CLASSIFICATION" == "FAIL" ]; then
        echo "========================================================================"
        echo "🔮 Oracle verdict: FAIL"
        echo "Detected $FAILED_CHECKS failed/cancelled check runs."
        echo "========================================================================"
        exit 1
    elif [ "$CLASSIFICATION" == "STALLED" ]; then
        echo "========================================================================"
        echo "🔮 Oracle verdict: STALLED"
        echo "Execution stall detected: check runs have not progressed across 3 cycles."
        echo "========================================================================"
        exit 2
    fi

    CYCLE=$((CYCLE + 1))
done

echo "========================================================================"
echo "🔮 Oracle verdict: TIMEOUT"
echo "Reached max cycles ($MAX_CYCLES) without a terminal classification."
echo "========================================================================"
exit 3