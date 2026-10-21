# Action-effectiveness correlation. Inputs are --slurpfile arrays.
def actionable($body): ($body // "") | test("(^|\\n)\\s*(fix|change|update|remove|add|please|must|should|address|resolve|request|review)\\b"; "i");
def bot_noise($body): ($body // "") | test("(usage limits|rate limit|review limit reached|auto-generated comment: release notes|<!-- action-effectiveness-ledger:)"; "i");
def event($kind;$id;$at): {kind:$kind,id:$id,at:$at};
([
  ($comments[0][] | select(((.body // "") | bot_noise(.)) | not) | select(actionable(.body)) | select(.created_at != null) | event("issue_comment";(.id|tostring);.created_at)),
  ($reviews[0][] | select(.state != "PENDING") | select(.submitted_at != null) | event("review";(.id|tostring);.submitted_at)),
  ($inline[0][] | select(((.body // "") | bot_noise(.)) | not) | select(actionable(.body)) | select(.created_at != null) | event("review_comment";(.id|tostring);.created_at))
] | sort_by(.at)) as $events
| ($commits[0] | map({sha:.sha, at:(.commit.committer.date // .commit.author.date)}) | map(select(.at != null)) | sort_by(.at)) as $cs
| [$events[] as $e
   | ($cs | map(select((.at|fromdateiso8601) > ($e.at|fromdateiso8601))) | .[0]) as $next
   | {kind:$e.kind,id:$e.id,at:$e.at,associated_commit_sha:($next.sha // null),associated_commit_at:($next.at // null),lag_minutes:(if $next then ((($next.at|fromdateiso8601)-($e.at|fromdateiso8601))/60|floor) else null end),relationship:(if $next then "FOLLOWED_BY_COMMIT" else "NO_LATER_COMMIT_IN_RANGE" end)}
  ]
| {all:., recent:(.[-32:])}
