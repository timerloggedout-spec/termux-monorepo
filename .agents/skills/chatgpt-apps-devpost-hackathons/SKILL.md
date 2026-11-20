---
name: devpost-hackathons
description: "Devpost Hackathons app for ChatGPT (by Devpost, Developer Tools, v4.0.1). Find hackathons, register, build, and submit without leaving ChatGPT, with a guided build assistant for ideation, scoping, and planning. Use when working the challenge-entries lane: discovering Devpost hackathons, checking entry requirements and deadlines, or walking a build from idea to submission on the ChatGPT surface."
metadata:
  version: "4.0.1"
  source: "https://chatgpt.com/plugins/plugin_asdk_app_6a330a7730c081919892632d5baaec58"
  plugin_id: "plugin_asdk_app_6a330a7730c081919892632d5baaec58"
  developer: "Devpost"
  category: "Developer Tools"
  intaked: "2026-11-20 (owner order; page copy crawled 2026-09-20)"
---

# Devpost Hackathons (ChatGPT app)

Find and submit to hackathons from inside ChatGPT. From Devpost, the leading hackathon platform. An optional build assistant walks through ideation, scoping, and planning to help ship a strong project.

## Component skills

- Guided Build Tool: Checklist
- Guided Build Tool: Ideate
- Guided Build Tool: PRD
- Guided Build Tool: Build
- Guided Build Tool: Scope
- Guided Build Tool: Spec
- Find Hackathon
- Hackathon Map

## Fleet use

- Surface: ChatGPT (the fleet's ChatGPT collaborator seat), not a local connector. The app runs where it is connected in ChatGPT; this record makes it discoverable at point of work.
- Lane: challenge entries — hackathon discovery, deadline and requirements checks, guided build flow (Ideate → Scope → Spec → PRD → Build → Checklist), submission via Devpost.
- Submissions and entries still land through the fleet's own routes and receipts discipline; the app is a discovery and build-assist surface, not the system of record. Coordinator state stays in the monorepo.

## Data note

When connected, ChatGPT may share relevant chats and memories with the Devpost app to provide context; Devpost's use of that data is governed by its own terms and privacy policy. Manage or disconnect in ChatGPT settings.
