# WorkFlows routing: optimizations (ranked)

Source: recon of .github/workflows and the bot review loop, 2026-11-17. Ranked by impact on the review loop.

## 1. One dedupe key for the Jules relay and the Linear sync
One review event currently fires two side effects: an @jules relay (agent-review-auto-jules.yml) and a Linear subtask (agent-feedback-linear-sync.yml). Write a hidden marker containing the review or comment ID back to the PR, and check it in both workflows before acting.

## 2. Relay cap per head SHA (max 3)
agent-review-auto-jules.yml has no cap. Each new bot review counts as new work, so review, relay, push, review repeats. Count prior relay comments for the current head.sha. At 3 or more, post one notice and exit. A new push changes head.sha, which resets the count.

## 3. Stamp gate in code, not only in docs
No provider stamp, no dispatch. Enforce this in the relay path instead of only documenting it.

## 4. Rotation on the relay path
No provider takes two consecutive dispatches for the same entry. Verify this in the relay path.

## 5. Retire or disable three duplicate Render webServices
termux-monorepo_render-webService v1, v2, and v3 all auto-deploy master-staging with ./setup.sh start commands and no health check. Dashboard action.

## 6. Keep the Jules issue lane label-only
agent-jules-on-issues.yml fires only on a jules label or an @jules comment from a collaborator. Filing an issue without either is safe.

## 7. Verify the #2672 gate before batch dispatch
PROVIDER-DISPATCH-MAP says the gate is both LIFTED and FAILED (contracts run 41303413675). Resolve this before promoting wired-unproven lanes.

## 8. Security: gate comment-triggered agents on author_association
deepseek-termux-agent.yml runs on any @deepseek comment in a public repo and forwards the text to a phone agent. Allow only OWNER, MEMBER, and COLLABORATOR. The same change applies to sweep-accountability.yml, ox-alpha-smoke.yml, and agent-ecc-tools-ops.yml.

## 9. Security: pass values through env in github-script
agent-review-auto-jules.yml interpolates steps.meta.outputs.head_ref and session_id directly into the script. Branch names can carry quotes, and head_ref can come from a fork. Use env plus process.env.

## Concrete patch shapes (adapt to the existing step names)

Gate (job level):
```yaml
if: contains(fromJSON('["OWNER","MEMBER","COLLABORATOR"]'), github.event.comment.author_association)
```

Env pass-through:
```yaml
env:
  HEAD_REF: ${{ steps.meta.outputs.head_ref }}
  SESSION_ID: ${{ steps.load-ctx.outputs.session_id }}
```

Relay cap (pseudocode):
```
count = number of comments containing '<!-- agent-auto-jules -->' AND head.sha
if count >= 3: post one notice; exit
else: post @jules; continue
```

Linear dedupe (pseudocode):
```
marker = '<!-- agent-linear-synced:' + comment_id + ' -->'
if marker exists on the PR comment: skip
else: create subtask; write marker back to the PR comment
```

See DOE-CONSIDERATIONS-2026-11-17.md for the DoE side of this work.
