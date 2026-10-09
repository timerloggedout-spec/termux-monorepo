#!/usr/bin/env bash
set -euo pipefail
echo "merge-queue-v3 event=${GITHUB_EVENT_NAME} sha=${GITHUB_SHA}"
mkdir -p /tmp/merge-queue
: > /tmp/merge-queue/candidates.ndjson
null_retries=0
list_ok=0
for attempt in 1 2 3 4; do
  if gh api --paginate -H 'Accept: application/vnd.github+json' "/repos/${GITHUB_REPOSITORY}/pulls?state=open&base=master&per_page=100" > /tmp/merge-queue/pr-pages.json; then
    list_ok=1
    break
  fi
  echo "merge-queue-v3 list attempt ${attempt} failed"
  sleep $((attempt * 5))
done
if [[ "$list_ok" != "1" ]]; then
  echo '[]' > /tmp/merge-queue/merge-promotion-queue.json
  echo "merge-queue-v3 deferred: list unavailable"
  exit 0
fi
jq -c 'if type == "array" then .[] | if type == "array" then .[] else . end elif type == "object" then . else empty end' /tmp/merge-queue/pr-pages.json | jq -s -c 'sort_by(.updated_at) | reverse | .[]' > /tmp/merge-queue/prs-sorted.ndjson
recent_cutoff=$(date -u -d '21 days ago' +%Y-%m-%dT%H:%M:%SZ)
while read -r pr; do
  number=$(jq -r '.number' <<<"$pr")
  head_sha=$(jq -r '.head.sha' <<<"$pr")
  head_ref=$(jq -r '.head.ref' <<<"$pr")
  title=$(jq -r '.title' <<<"$pr")
  draft=$(jq -r '.draft' <<<"$pr")
  mergeable=$(jq -r '.mergeable' <<<"$pr")
  mergeable_state=$(jq -r '.mergeable_state // "unknown"' <<<"$pr")
  updated=$(jq -r '.updated_at' <<<"$pr")
  [[ "$number" =~ ^[0-9]+$ ]] || continue
  [[ -n "$head_sha" && "$head_sha" != "null" ]] || continue
  if [[ "$updated" < "$recent_cutoff" ]]; then
    jq -cn --argjson number "$number" --arg title "$title" --arg head_ref "$head_ref" --arg head_sha "$head_sha" --arg updated "$updated" --arg mergeable "$mergeable" --arg mergeable_state "$mergeable_state" '{number:$number,title:$title,head_ref:$head_ref,head_sha:$head_sha,updated_at:$updated,disposition:"HOLD",reason:"stale-observer-budget",repo_gate:"skipped",termux_smoke:"skipped",active_changes_requested:0,hard_failures:0,pending_checks:0,mergeable:$mergeable,mergeable_state:$mergeable_state,behind:"skipped",compare_status:"skipped"}' >> /tmp/merge-queue/candidates.ndjson
    continue
  fi
  if [[ "$mergeable" == "null" || -z "$mergeable" ]]; then
    detail=$(gh api -H 'Accept: application/vnd.github+json' "/repos/${GITHUB_REPOSITORY}/pulls/${number}")
    mergeable=$(jq -r '.mergeable' <<<"$detail")
    mergeable_state=$(jq -r '.mergeable_state // "unknown"' <<<"$detail")
  fi
  if [[ "$mergeable" == "null" || -z "$mergeable" ]] && (( null_retries < 36 )); then
    null_retries=$((null_retries + 1))
    sleep 2
    detail=$(gh api -H 'Accept: application/vnd.github+json' "/repos/${GITHUB_REPOSITORY}/pulls/${number}")
    mergeable=$(jq -r '.mergeable' <<<"$detail")
    mergeable_state=$(jq -r '.mergeable_state // "unknown"' <<<"$detail")
  fi
  reviews=$(gh api -H 'Accept: application/vnd.github+json' "/repos/${GITHUB_REPOSITORY}/pulls/${number}/reviews?per_page=100")
  active_changes=$(jq '[.[] | select(.state == "CHANGES_REQUESTED")] | length' <<<"$reviews")
  checks=$(gh api -H 'Accept: application/vnd.github+json' "/repos/${GITHUB_REPOSITORY}/commits/${head_sha}/check-runs?per_page=100")
  repo_gate=$(jq -r '[.check_runs[] | select(.name == "hygiene + portability gate" or .name == "repo gate") | .conclusion] | last // "missing"' <<<"$checks")
  termux_smoke=$(jq -r '[.check_runs[] | select(.name == "agentic termux smoke" or .name == "termux smoke") | .conclusion] | last // "missing"' <<<"$checks")
  hard_failures=$(jq '[.check_runs[] | select(.status == "completed" and (.conclusion == "failure" or .conclusion == "timed_out" or .conclusion == "action_required") and (.name | test("Vercel|vercel|DeepSeek|Devin") | not))] | length' <<<"$checks")
  pending=$(jq '[.check_runs[] | select(.status != "completed")] | length' <<<"$checks")
  behind="unknown"
  compare_status="unknown"
  if compare=$(gh api -H 'Accept: application/vnd.github+json' "/repos/${GITHUB_REPOSITORY}/compare/${GITHUB_SHA}...${head_sha}" 2>/dev/null); then
    behind=$(jq -r '.behind_by // "unknown"' <<<"$compare")
    compare_status=$(jq -r '.status // "unknown"' <<<"$compare")
  fi
  disposition="HOLD"
  reason=""
  if [[ "$draft" == "true" ]]; then reason="draft"
  elif [[ "$mergeable" == "null" || -z "$mergeable" ]]; then reason="mergeable-unknown"
  elif [[ "$mergeable" != "true" ]]; then reason="not-mergeable-${mergeable_state}"
  elif (( active_changes > 0 )); then reason="active-changes-requested"
  elif (( hard_failures > 0 )); then reason="completed-check-failure"
  elif (( pending > 0 )); then reason="checks-pending"
  elif [[ "$repo_gate" != "success" ]]; then reason="repo-gate-${repo_gate}"
  elif [[ "$termux_smoke" != "success" ]]; then reason="termux-smoke-${termux_smoke}"
  elif [[ "$behind" == "unknown" || -z "$behind" ]]; then reason="base-compare-unknown"
  elif [[ "$behind" != "0" ]]; then reason="base-behind-${behind}"
  else disposition="CANDIDATE"; reason="all-promotion-preconditions-observed"
  fi
  jq -cn --argjson number "$number" --arg title "$title" --arg head_ref "$head_ref" --arg head_sha "$head_sha" --arg updated "$updated" --arg disposition "$disposition" --arg reason "$reason" --arg repo_gate "$repo_gate" --arg termux_smoke "$termux_smoke" --argjson active_changes "$active_changes" --argjson hard_failures "$hard_failures" --argjson pending "$pending" --arg mergeable "$mergeable" --arg mergeable_state "$mergeable_state" --arg behind "$behind" --arg compare_status "$compare_status" '{number:$number,title:$title,head_ref:$head_ref,head_sha:$head_sha,updated_at:$updated,disposition:$disposition,reason:$reason,repo_gate:$repo_gate,termux_smoke:$termux_smoke,active_changes_requested:$active_changes,hard_failures:$hard_failures,pending_checks:$pending,mergeable:$mergeable,mergeable_state:$mergeable_state,behind:$behind,compare_status:$compare_status}' >> /tmp/merge-queue/candidates.ndjson
done < /tmp/merge-queue/prs-sorted.ndjson
if [[ ! -s /tmp/merge-queue/candidates.ndjson ]]; then echo '[]' > /tmp/merge-queue/merge-promotion-queue.json; else jq -s 'map(select(type == "object" and has("number"))) | sort_by([.disposition != "CANDIDATE", .updated_at])' /tmp/merge-queue/candidates.ndjson > /tmp/merge-queue/merge-promotion-queue.json; fi
{
  echo '# Merge Promotion Queue'
  echo
  echo "Generated from SHA ${GITHUB_SHA} at $(date -u +%Y-%m-%dT%H:%M:%SZ)."
  echo
  echo '> Observer-only: this workflow never merges. PRs older than 21 days are HOLD stale-observer-budget (run 37990430709 on f5b8bdac).'
  echo
  echo '| PR | Disposition | hygiene gate | termux smoke | behind | SHA | Reason |'
  echo '|---:|---|---|---|---:|---|---|'
  jq -r '.[] | "| #\(.number) | \(.disposition) | \(.repo_gate) | \(.termux_smoke) | \(.behind // "") | \(.head_sha[0:12]) | \(.reason) |"' /tmp/merge-queue/merge-promotion-queue.json
} >> "$GITHUB_STEP_SUMMARY"
