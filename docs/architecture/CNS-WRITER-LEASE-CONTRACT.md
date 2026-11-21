# CNS Writer Lease Contract

**Contract status:** Proposed; enforcement service unimplemented  
**CNS work item:** CNS-11  
**Scope key:** `(repository, pull_request, revision)`

## 1. Purpose

Provide one enforceable write owner for each repository pull request revision across agent, model, provider, and automation lanes. The lease coordinates corrective writes while preserving independent read, review, and evidence collection.

## 2. Canonical resource identity

A lease key identifies one exact revision:

```text
lease_key = repository_id + ":" + pull_request_number + ":" + revision_sha
```

The resource record carries:
- Canonical repository identity.
- Pull request number.
- Full 40-character source revision SHA.
- Owner identity: provider, model, agent, adapter, and invocation.
- Monotonic lease epoch.
- Acquisition, renewal, expiry, and release timestamps.
- Immutable evidence receipt reference.

Repository, pull request, and revision remain separate identity dimensions. A new revision receives a new lease key.

## 3. Lease lifecycle

1. **Acquire:** A provider requests a lease for the exact resource key. The authority performs an atomic compare-and-swap from unowned or expired to acquired.
2. **Fence:** The authority issues a monotonically increasing epoch. Every write adapter presents the current epoch and owner identity.
3. **Renew:** The current owner renews before expiry while the source revision remains unchanged.
4. **Write:** A provider adapter validates owner, epoch, expiry, and current revision immediately before each mutation.
5. **Release:** The owner releases after the bounded write session completes or aborts.
6. **Recover:** A recovery actor re-reads the canonical PR head and evidence, waits for expiry plus the configured heartbeat window, then acquires a new epoch.
7. **Reject:** Competing, stale-epoch, expired, or wrong-revision writes produce a rejected-attempt receipt.

## 4. Required enforcement properties

- Atomic acquisition and renewal.
- Monotonic fencing epochs.
- Revision-bound lease keys.
- Expiry and bounded renewal.
- Revalidation immediately before mutation.
- Append-only acquisition, renewal, rejection, release, and recovery receipts.
- Provider adapter enforcement for every write-capable integration.
- Explicit read-only mode for providers without lease enforcement.
- Human escalation for uncertain ownership and abandoned sessions.

A coordination comment, label, workflow run, or advisory receipt records intent. It does not enforce a global single-writer property by itself.

## 5. GitHub Actions coverage

GitHub Actions concurrency groups serialize only workflows that share the same group key. They provide useful internal workflow coordination and do not establish provider-wide fencing.

The existing GitLab reconciliation workflow has its own fixed concurrency group and preserves GitHub master as the promotion spine. The Jules handoff and relay controls govern their own lanes. CNS-11 must inventory and migrate every repo-controlled writer workflow to a shared revision-keyed gate, then add the provider adapter enforcement boundary.

## 6. Provider enforcement boundary

The full contract requires every write-capable provider to:
- Obtain a lease before branch or PR mutation.
- Present the active epoch at the write boundary.
- Revalidate the current revision before committing.
- Record the actual mutation receipt and resulting SHA.

Providers with direct credentials that bypass the lease gateway remain outside the enforcement perimeter. Restrict those credentials to read-only or route writes through a governed adapter before declaring global single-writer coverage.

## 7. Required receipt states

The machine-readable envelope is defined in `docs/schemas/cns-writer-lease-receipt.schema.json`.

`acquired`, `renewed`, `released`, `expired`, `rejected`, `recovered`.

Each receipt binds:
- `lease_key`
- `repository_id`
- `pull_request_number`
- `revision_sha`
- `owner.provider_id`
- `owner.agent_id`
- `owner.adapter_id`
- `epoch`
- `state`
- `observed_at`
- `expires_at`
- `evidence_ref`

Fencing tokens remain transient authorization material. Receipts record the epoch and owner reference, not the secret token.

## 8. Acceptance tests

1. Two simultaneous acquisitions for one key yield exactly one owner.
2. A stale epoch is rejected after a newer epoch is issued.
3. A lease for revision A cannot mutate revision B.
4. An expired lease cannot write before recovery.
5. A renewal by a different owner is rejected.
6. Release makes the key available for a new epoch.
7. Provider adapters reject writes without a valid lease.
8. Read-only providers continue to collect evidence without acquiring write leases.
9. Every accepted and rejected mutation attempt produces an attributable receipt.
10. A cross-provider test demonstrates one active owner across the supported provider set.

## 9. Current status

The repository has documented scope identity, GitHub Actions concurrency, governed GitLab reconciliation, and Jules handoff controls. It has no universal atomic lease authority or provider-wide fencing adapter.

**Current enforcement claim:** Internal workflow serialization is partial. Cross-provider single-writer enforcement is unverified. CNS-11 remains open until the authority service and all write-capable adapters pass the acceptance tests.
