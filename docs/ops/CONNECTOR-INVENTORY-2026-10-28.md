# Connector Inventory — 2026-10-28

Compiled from the CONNECTOR.md (and connector.yaml where present) of every connector directory, first ~40 lines each. Capability lines are taken from the docs; use-case lines are concrete fleet applications of those capabilities. Status sources: the connector's own doc/yaml text, or the platform catalog annotation shown to this lane (marked as such, dated 2026-10-28) — otherwise NOT ESTABLISHED (a doc existing does not prove a live connection).

- System connectors (`/opt/hatch/connectors/`): **68**
- Custom connectors (`~/workspace/custom-connectors/`): **3**
- **Total: 71**

| Connector | Kind | Status | Capabilities / use cases |
|---|---|---|---|
| agoda | system | NOT ESTABLISHED | Search stays, flights, tours, attraction tickets; booking continues on Agoda's site via returned link. Use: travel search when other routes lack coverage. |
| apple_healthkit | system | NOT ESTABLISHED | Read iPhone-synced Apple Health metrics, samples, sleep, workouts; delete with approval. Use: health reviews from iOS devices. |
| asana | system | NOT ESTABLISHED | Team projects and tasks via Asana's official MCP. Use: work-task tracking outside the repo. |
| box | system | NOT ESTABLISHED | Personal/company files via Box hosted MCP + REST for transfers, moves, deletions. Use: file storage and sharing. |
| calendly | system | NOT ESTABLISHED | User's booking links, event types, booked meetings. Use: scheduling intake and meeting checks. |
| canva | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Designs, images, assets, exports, folders, comments, brand templates/kits, resize, autofill via Canva MCP. Use: graphics, posters, social posts, decks. |
| dropbox | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | User's files via Dropbox MCP + file API; find, read, upload, download, organize, share, file requests. Use: file transfer and archival. |
| duffel | system | NOT ESTABLISHED | Search, book, cancel complete flight itineraries; fare recheck on booked trips. Use: flight booking without a user login; pays via Link by Stripe. |
| evernote | system | NOT ESTABLISHED | Notes, notebooks, Spaces, tags, tasks, attachments via Evernote MCP. Use: note search and organization. |
| facebook_cli | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Friends, profiles, posts, groups, events, stories, saved items; publish personal posts/comments; Pages; Marketplace search/manage. Use: Facebook presence and Marketplace work. |
| figma | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Inspect designs/FigJam, components, variables, libraries, assets; design-to-code; edit designs; diagrams. Use: UI design work for repo apps and pages. |
| flightaware | system | NOT ESTABLISHED | Dated schedules, live status, positions, tracks, airport activity; no account/API key (managed service). Use: flight tracking. |
| function_health | system | NOT ESTABLISHED | Read lab biomarker observations and clinician consultation notes via FHIR API (read-only). Use: lab-result review. |
| ghl | system | NOT ESTABLISHED | HighLevel CRM/marketing platform, organized into sub-accounts, via its MCP service. Use: CRM and marketing ops for small-business clients. |
| github | system | connected (platform catalog) but DENY by owner order — fleet route is custom.github-pat | Repos, files, issues, PRs via GitHub's official MCP. Use: NONE in this fleet by owner order — DENY; all GitHub work goes through custom.github-pat. |
| gmail | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Search, read, count mail and attachments; draft, send, reply, forward with approval; label, archive, trash, unsubscribe. Use: the user's mailbox work. |
| google_calendar | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Read calendars and free/busy; schedule, change, cancel events with Meet links and guest notifications. Use: scheduling. |
| google_contacts | system | NOT ESTABLISHED | User's Google address book: search, create, edit, delete contacts. Use: contact lookup and upkeep. |
| google_docs | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Read, create, edit Google Docs, incl. notes/notebooks kept as Docs. Use: document drafting. |
| google_drive | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Find, upload, download, organize, share Drive files. Use: file management in Google storage. |
| google_forms | system | NOT ESTABLISHED | Forms API via the Workspace wrapper: read/create forms and responses (per API surface). Use: surveys and intake forms. |
| google_health_connect | system | NOT ESTABLISHED | Read Android-synced Health Connect metrics, samples, sleep, workouts; delete with approval. Use: health data from the user's Android phone. |
| google_sheets | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Create, read, edit Sheets: cells, formulas, tabs, formatting. Use: spreadsheets, registries, trackers. |
| google_slides | system | NOT ESTABLISHED | Slides API via the Workspace wrapper: read/edit presentations. Use: deck work. |
| google_tasks | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Find and manage Google Tasks lists/tasks, due dates, subtasks, ordering, completion. Use: lightweight todos in Google. |
| granola | system | NOT ESTABLISHED | Read past meeting notes, summaries, transcripts (read-only; no scheduling). Use: meeting follow-up from real notes. |
| healthex | system | NOT ESTABLISHED | Gather the user's records from healthcare providers (read-only MCP). Use: consolidated medical-record review. |
| instagram | system | NOT ESTABLISHED | Search accounts; read profiles, posts, comments, stories, feeds, saved items, insights; publish/schedule stories, posts, reels, carousels; manage collections and profile. Use: Instagram presence. DMs are instagram_messages. |
| instagram_messages | system | NOT ESTABLISHED | Read/send Instagram DMs and manage pending message requests; connection separate from instagram. Use: DM conversations. |
| klaviyo | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Email/SMS campaigns, flows, lists, segments, subscriptions, reports; send approved campaigns. Use: marketing automation. |
| linear | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Issues, projects, comments, labels, cycles, documents via Linear MCP. Use: issue tracking; also connected on the Jules side. |
| lovable | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Create, edit, deploy Lovable apps; read code/messages; manage visibility, knowledge, databases. Use: rapid app prototyping. |
| messenger_read | system | NOT ESTABLISHED | Read, search, send in the user's personal Messenger account (sends as the user); call history, reactions, edits, Marketplace threads. Use: Messenger conversations. Despite the name, it can send. |
| meta_ads | system | NOT ESTABLISHED | Facebook/Instagram ads: ideas and creative, spend/results, campaigns, audiences, catalogs, pixels, experiments; create paused campaigns; policy answers. Use: ad-account management. |
| meta_catalog_search | system | NOT ESTABLISHED | Search Meta's product catalog across merchants: prices, images, variants, checkout eligibility. Needs no sign-in. Use: product search for shopping. |
| moneyforward_me | system | NOT ESTABLISHED | Read linked bank, card, securities, e-money accounts (read-only). Use: finance overview in Money Forward ME. |
| muse_mail | system | NOT ESTABLISHED | Muse's own mailbox (never the user's): mail workers send/receive through it. Use: agent-originated email. |
| notion | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Search, read, edit pages, databases, notes, comments in the user's Notion workspace. Use: knowledge organization. |
| onepassword | system | NOT ESTABLISHED | Pick saved logins from 1Password to sign in to websites in the Muse browser; cannot browse the vault. Use: browser sign-ins. |
| opentable | system | NOT ESTABLISHED | Live restaurant availability; make, change, cancel reservations. Use: restaurant booking. |
| outlook_calendar | system | NOT ESTABLISHED | Personal Microsoft and Microsoft 365 calendars. Use: scheduling on Microsoft accounts. |
| outlook_contacts | system | NOT ESTABLISHED | Address books of personal Microsoft and M365 accounts. Use: contact lookup on Microsoft accounts. |
| outlook_mail | system | NOT ESTABLISHED | Personal Microsoft and M365 mailboxes; the user's mail, separate from Muse Mail. Use: Outlook mailbox work. |
| peloton | system | NOT ESTABLISHED | Search Peloton class catalog and manage classes on the user's schedule (cannot read completed workouts). Use: workout scheduling. |
| philips_hue | system | NOT ESTABLISHED | Control Hue lights via Hue Remote API v2 through the user's bridge. Use: home lighting control. |
| places | system | NOT ESTABLISHED | Find physical places/businesses; addresses, hours, ratings, reviews, photos; identify a place from photos. No account. Use: local discovery and trip stops. |
| plaid | system | NOT ESTABLISHED | Read linked bank, card, loan, investment accounts: balances, transactions, spending, bills/subscriptions, liabilities, holdings (read-only, masked numbers). Use: financial planning. |
| printify | system | NOT ESTABLISHED | Print-on-demand products and fulfillment for a merchant's shops, via personal access token. Use: merch/POD store ops. |
| quickbooks | system | NOT ESTABLISHED | User's company via Intuit's official MCP; tools run through call-tool. Use: business accounting reads/writes per tool surface. |
| replit | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Find, create, update Replit apps from a description; ask about them; publish. Use: quick app builds/deploys. |
| shop-pay | system | NOT ESTABLISHED | Consumer wallet accepted by Shopify merchants; pays checkouts with the saved Shop Pay card after native approval. Use: Shopify checkout payment. |
| shopback_mcp | system | NOT ESTABLISHED | ShopBack cashback/offers, hotel/flight prices with cashback, promos, eCards, outlets; create cashback-tracked links. Use: savings on shopping/travel. |
| shopify | system | NOT ESTABLISHED | Run a Shopify store via merchant MCP: products, collections, inventory, orders, customers, discounts, reports. Use: store operations (merchant side). |
| shopify-ucp | system | NOT ESTABLISHED | Buy eligible Shopify products from Meta Catalog via direct checkout/carts, paid with a connected wallet; track/cancel orders. Use: shopper-side checkout. |
| slack | system | NOT ESTABLISHED | User's work chat via Slack MCP; posts appear under the user's own name. Use: workplace messaging. |
| spotify | system | NOT ESTABLISHED | Search/play music, audiobooks, podcasts; manage library, playlists, playback; manage Save to Spotify shows. Use: music and playlist work. |
| stripe | system | NOT ESTABLISHED | Merchant Stripe: customers, products, coupons, payments, invoices, subscriptions, refunds, disputes, balances, payouts. Use: business payments admin. |
| stripe-link | system | NOT ESTABLISHED | Link by Stripe consumer wallet: funds one-time virtual cards after purchase approval. Use: shopper payments in Duffel/Shopify UCP/browser checkouts. |
| tailscale | system | NOT ESTABLISHED | Built-in client joins this VM to the user's tailnet (device name `muse`); reach private TCP services via the built-in proxy. Use: reaching home/LAN services. |
| tessie | system | NOT ESTABLISHED | Tesla vehicles via Tessie: list vehicles, read state, send supported commands, using the user's Tessie API token. Use: vehicle status/control. |
| threads | system | NOT ESTABLISHED | Profiles, posts, replies, feeds, activity, insights, trends, search; publish posts; feed-ranking feedback. Use: Threads presence. DMs are threads_messages. |
| threads_messages | system | NOT ESTABLISHED | Read and send Threads DMs; connection separate from threads. Use: Threads conversations. |
| ticketmaster | system | NOT ESTABLISHED | Find events, compare tickets/seats/prices, get checkout link; cannot buy (purchase continues in browser). No setup needed. Use: event ticket search. |
| todoist | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Tasks, projects, sections, comments, labels, filters, reminders via Todoist MCP. Use: personal task management. |
| vercel | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Deploy sites/apps; inspect projects, deployments, logs; change settings, env vars, domains, DNS; buy domains/upgrades with approval. Use: hosting for repo web surfaces. |
| withings | system | NOT ESTABLISHED | Read Withings account: activity, sleep, workouts; body measurements under a separate permission. Use: health metrics. |
| zapier | system | NOT ESTABLISHED | Zapier MCP in agentic mode: one connection reaches actions the user set up across their Zapier apps. Use: coverage for apps with no dedicated connector. |
| zoom | system | connected (platform catalog annotation, 2026-10-28; verify before relying on live data) | Meetings, recordings, transcripts, summaries; Team Chat, Canvas, Tasks, Whiteboard, Revenue Accelerator via Zoom MCP. Use: meeting management and follow-up. |
| custom.github-pat | custom | Registered (per doc) | GitHub REST via the user's classic PAT (MUSE_ADMIN_GH), helper github_pat.py: rate limits, user, repos, PRs, generic api for writes; no per-call approval cards. Use: ALL fleet GitHub work (fleet rule; built-in github connector is DENY). |
| custom.jules | custom | Registered (per doc) | Google Jules REST via API key, helper jules.py: list/read sessions, activities, full census, approve-plan, send-message. Use: monitoring and steering Jules coding sessions. |
| custom.stackoverflow-agents | custom | connected-verified 2026-10-28 (connector.yaml) | SOFA MCP (agents.stackoverflow.com/mcp), OAuth public client + PKCE, helper sofa.py: 28 tools — search, get_post, my_posts, guidance, playbooks; granted scopes read + identity + offline only. Use: agent knowledge exchange bound to the owner's existing SOFA agent. |

## Notes

- **Status discipline:** system CONNECTOR.md files carry no in-file connected annotation; statuses above come from the platform catalog annotation (2026-10-28) where one exists, else NOT ESTABLISHED. Live-ness must still be established per connector with its `status` command before relying on it.
- **github vs custom.github-pat:** the built-in github connector is set to DENY by the owner; custom.github-pat is the fleet's only GitHub route.
- **Split pairs (separate connections):** instagram / instagram_messages; threads / threads_messages; shopify (merchant) vs shopify-ucp (shopper checkout) vs shop-pay / stripe-link (wallets); gmail (user) vs muse_mail (Muse) vs outlook_mail (user, Microsoft).
- **Similar names, different backends:** apple_healthkit (iOS) vs google_health_connect (Android) share the health-cli with a --provider flag; function_health (labs) and healthex (provider records) are separate health sources.
- **messenger_read** is named read but its doc covers sending as the user.
- **No-account connectors per their docs:** flightaware (managed service), meta_catalog_search, places, ticketmaster — usable without a user connection, which is distinct from a "connected" status.
- No connector directory was missing a CONNECTOR.md.
