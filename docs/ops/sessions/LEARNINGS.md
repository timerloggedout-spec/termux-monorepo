# Session Learnings

## 2026-11-23 — Dynamic cadence awareness and security-learning cohorts

### Cadence RECON

- Read `schedule`, `timeout_secs`, and `cron:timing-window` as independent fields. A 2h timeout describes one run's execution budget; it does not establish a 2h recurrence.
- Treat `Dynamic` as the canonical decision mode. Derive each next-run time from current source watermarks, freshness, run outcomes, capacity/quota, queue pressure, and dependency demand.
- Coordinate related producers through one registry-owned cadence decision while retaining separate producer identities, run/skip receipts, results, consumers, and encryption state.
- Confirm propagation with live VM scheduler read-back and workflow/config read-back. Compare receipts and watermarks over at least 24h before recording parity.
- The 2026-11-23 BRR and repo-export descriptors were both daily and had different run windows. Their 3600s/7200s timeout and timing-window metadata did not prove a 45m recurrence. See [Adaptive Dynamic Awareness](../ADAPTIVE-DYNAMIC-AWARENESS.md).

### Pentest / CTF learning

- Route security practice through the agent team's existing Scout security-evaluation cohort and explicitly authorized CTF or lab environments.
- Start with OverTheWire Bandit for Linux/SSH fundamentals; progress through PicoCTF or pwn.college, PortSwigger Web Security Academy, and OffSec PEN-200 as appropriate to the learner's goals.
- Store each exercise's target allowlist, scope, permitted methods, time window, rate limits, evidence-handling rules, and stop conditions with its task.
- Convert validated findings into remediation tasks and defensive regression tests. A cohort label is a learning route, not an authorization grant.
- OffSec's current OSCP+ exam guide prohibits AI chatbots during the exam and reporting phase; exam work remains independent.

### Sources

- [OverTheWire Bandit](https://overthewire.org/wargames/bandit/)
- [OffSec PEN-200](https://www.offsec.com/courses/pen-200/)
- [OffSec OSCP+ Exam Guide](https://help.offsec.com/hc/en-us/articles/360040165632-OSCP-Exam-Guide)
- [Agent Team Control Plane](../../architecture/AGENT-TEAM-CONTROL-PLANE.md)
- [Adaptive WAIT](../../../.agents/skills/adaptive-wait/SKILL.md)
