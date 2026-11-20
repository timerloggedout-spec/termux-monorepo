# Proposal Manifest — linguist-contact-projections

| Field | Value |
|---|---|
| Proposal ID | `linguist-contact-projections` |
| Status | `executing` |
| Owner | `timerloggedout-spec` |
| Implementer | `Manus AI` |
| Scope | Deterministic human-source, L33t display, and machine projection parity across root and ICM agent contact documents. |
| Base | `master-staging` |
| Related | #274, #275, #154, #177, #117, #175 |

## Authority Boundary

`*.hum.md` files are canonical human sources. Generated `.md` contact surfaces are deterministic Linguist projections and must not be hand-edited. This proposal uses a public bootstrap lexicon; it neither commits nor emulates a production private mapper.

The scope includes `README`, `AGENTS`, `CLAUDE`, and `CONTEXT` contact documents in the root and `docs/icm/` tree. It excludes credentials, private mapper custody, remote A2A transport, CID/CEDARscript execution, and workflow changes.
