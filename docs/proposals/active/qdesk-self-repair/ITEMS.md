# QDesk self-repair — itemized work

The originating proposal is PROPOSAL.md. Items below preserve its seven-stage SIE loop.

| Item | Stage | Deliverable | Acceptance evidence |
|---|---|---|---|
| QSR-01 | Observe | Batch intake of failing master runs, stale feeds and open Desk issues | One deduplicated QUE item per workflow/error signature |
| QSR-02 | Research | Root-cause diagnosis note | Run URL, source SHA and relevant history receipts |
| QSR-03 | RFP | Fix specification and replay plan | Acceptance tests plus a replay of the failing run |
| QSR-04 | Implement | At least two candidate patches | Candidate provenance; no self-selected winner |
| QSR-05 | Evaluate | Independent DoE verification | Replay CI evidence and DoE reviewer check |
| QSR-06 | Promote | Authority-gated additive change | Owner packet for destructive, secret, spend or third-party effects |
| QSR-07 | Learn | Outcome and role-weight ledger update | Verified outcome; regression recorded with negative adjustment |

## Non-goals
- Keep correctness claims unverified until independently checked.
- Keep winning-treatment selection with the independent DoE reviewer.
- Require Owner approval for protected change classes.
