# smods — live custom-adapted submodules

The root .gitmodules file is the source of truth for live gitlinks. This directory contains reviewed custom forks only; each live pin requires an immutable commit, compatibility evidence, and passing dual gates.

## Pinecone candidate

| Field | Value |
|---|---|
| Intended path | refTemplates/smods/pg_pinecone_fork |
| Upstream | https://github.com/pinecone-io/pg_pinecone |
| Reviewed upstream commit | d860f6fd3a21733d75ed2cde2b5b5e71e79bd3ac |
| License | Apache-2.0 |
| State | candidate — custom fork pending |
| DoE | experiments/doe/pinecone-vector-store/DESIGN.json |

The upstream source is catalogued in refTemplates/18_Vector_Databases/pinecone/. The current GitHub connector provides repository reads and ordinary content writes, but no fork-creation operation. The live gitlink is held until timerloggedout-spec/pg_pinecone_fork exists and passes the submodule integrity, compatibility, and dual-gate checks. Existing Pinecone REST integration remains active independently.
