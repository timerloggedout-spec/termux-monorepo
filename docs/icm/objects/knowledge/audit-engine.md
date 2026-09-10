# AuditEngine (Ethics Engine) — Psychometric Assessment of LLMs

**Source fork:** `refTemplates/smods/AuditEngine_fork` (pending gitlink)  
**Owned fork:** https://github.com/timerloggedout-spec/AuditEngine_fork  
**Upstream:** https://github.com/RinDig/AuditEngine  
**Live demo (upstream):** https://ethicsengine.eduba.io

## What it is

Web application for psychometric assessment of Large Language Models. Applies validated instruments (RWA, LWA, MFQ, NFC, BFI-10, SDO-7, RSES, GSE, LOT-R, …) across providers and personas, including visual-stimulus assessment for vision-capable models.

## Why it belongs near the monorepo ICM surface

- Supplies structured **evidence** about model dispositions under controlled framings — complementary to filesystem-memory cost evidence and provider-routing governance.
- Patterns (scale validation, persona variation, exportable CSV/JSON jobs) can inform future evaluation lanes without becoming a monorepo runtime dependency.

## Boundary (hard)

- No automatic Vercel/Railway deploy from this monorepo.
- No provider API keys in monorepo secrets unless a separate Tier-4 proposal is accepted.
- Fork is reference + adapt surface; operative assessments stay outside control plane until authorized.

## Native use

| Surface | Role |
|---|---|
| This card | Operator summary + boundary |
| `docs/proposals/active/auditengine-adapt/` | Adapt checklist |
| Owned fork | Customization / upstream sync |

## Stack (upstream)

- Frontend: Next.js 14+ (App Router, TypeScript, Tailwind)
- Backend: FastAPI (Python, async)
