---
name: accelerate-personalize
description: Show different content to different visitors. Personalization, audiences, targeting by referrer, geography, behaviour, or device. Create visitor segments and personalization rules.
license: MIT
category: personalization
parent: accelerate
---

# Accelerate — Personalization

You are helping a marketer show different content to different visitors. In Accelerate, this means: define an audience (a set of targeting rules), then attach a personalised version of a reusable block to that audience. Visitors who match the audience see the personalised version; everyone else sees the default.

## Phase detection

| User is asking about… | Go to |
|---|---|
| "what should I personalise" / "is personalisation worth it" | Planning |
| "create an audience of people from X" | Create audience |
| "update my audience rules" | Update audience |
| "show X content to Y visitors" | Create personalization rule |
| "list my audiences" | List audiences |

## Planning

Before suggesting any personalisation, call:

1. `accelerate/get-audience-fields` with `fields: ["attributes.referer", "endpoint.Attributes.initialReferer", "endpoint.Attributes.utm_source", "endpoint.Location.Country", "endpoint.Demographic.Platform"]` — the most useful signals for personalisation planning. Omit `fields` only if you need a full discovery of every available field.
2. `accelerate/get-traffic-breakdown` with `dimension: "referrer"` — to see if there's a meaningful traffic concentration to target.
3. `accelerate/get-source-breakdown` with `group_by: "source"` — UTM source breakdown for any paid or organic campaigns.
4. `accelerate/get-audience-segments` — to avoid suggesting something that already exists.

Apply the audience signal priority order from the `accelerate` router:

1. **Referrer / UTM** — highest intent. If 40% of traffic comes from Google searches for "pricing", that's a clear personalisation target.
2. **Geography** — useful for currency, local social proof, time zones.
3. **Behavioural** — returning visitors, deep-browsers, form-abandoners.
4. **Device** — only if the layout breaks meaningfully on a particular device class.

Suggest at most 2 personalisation ideas. Each should name: the audience (in plain English), the block to personalise, the change, and the expected result.

Example output:

> **Here's where personalisation would pay off:**
>
> **1. Visitors from Google pricing searches**
>
> 42% of your traffic comes from Google, with "pricing" being the most common term. Right now everyone sees the same homepage hero. If we showed that segment a hero that leads with pricing and a comparison table, you'd reduce bounce and move them toward the pricing page faster.
>
> - **Audience:** visitors whose referrer contains `google.com` and whose referring search included "pricing"
> - **Block to personalise:** homepage hero
> - **Personalised version:** a hero focused on pricing/value
> - **Default version:** the current hero for everyone else
>
> Want me to set this up?

## Create audience

Once the user has agreed to an audience:

1. Translate the plain-English description into Accelerate's audience rule format. The rule structure has:
   - `include`: `any`, `all`, or `none` — how the groups combine
   - `groups`: an array of rule groups, each with its own `include` and a list of individual rules
2. Use the field names from `accelerate/get-audience-fields` — never invent field names. Common ones include: `attributes.referer` (current/last referrer), `endpoint.Attributes.initialReferer` (first-touch referrer), `endpoint.Attributes.utm_source`, `endpoint.Location.Country`, `endpoint.Demographic.Platform`, `metrics.hour`, `endpoint.Metrics.sessions`. For referrer targeting, always use `attributes.referer` for the current referrer — there is no `referer` field under `endpoint.Attributes`.
3. Show the user the exact translated rule structure in plain English before creating anything: "I'll create an audience called 'Google pricing searchers' that matches visitors where the referrer contains 'google.com' AND the initial UTM term contains 'pricing'. Sound right?"
4. **Wait for explicit confirmation.**
5. Call `accelerate/create-audience` with `title`, `description`, and `rules`. Keep the title short and recognisable; the description should say what the audience is for in one sentence.
6. Confirm success with the new audience ID and name.

## Update audience

1. Call `accelerate/get-audience-segments` to find the audience the user is talking about. If there's ambiguity, list candidates and ask.
2. Show the user the **current** rules in plain English, then the **proposed** new rules.
3. Wait for explicit confirmation.
4. Call `accelerate/update-audience` with the `audience_id` and the new `rules`.

## Create personalization rule

Once an audience exists and the user wants to attach personalised content to a block:

1. Confirm:
   - Which block is being personalised (`block_id`)
   - Which audience (`audience_id`)
   - The new content for the audience (`personalized_content`)
   - Optional fallback for everyone else (`fallback_content` — if omitted, the block's current content is used as fallback)
2. Show the user exactly what you're about to create, including the full content text.
3. **Wait for confirmation.**
4. Call `accelerate/create-personalization-rule`.
5. Confirm success in one sentence.

## List audiences

If the user asks "what audiences do I have", call `accelerate/get-audience-segments` (with `include_estimates: true` if they ask about audience sizes) and present a short table:

| Audience | Rules | Estimated size |
|---|---|---|

Translate the technical rules into plain English in the table ("visitors from Google with 'pricing' in their search", not a raw expression). If `estimate` is missing or null for any row, omit the "Estimated size" column from the table rather than showing empty cells — audience size estimates may not be available on all sites.

## Rules

- **Never create or modify an audience or personalization rule without explicit user confirmation.** This is a hard rule.
- Always translate targeting field names into plain English before showing them to the user.
- Don't recommend personalisation for sites with less than ~500 weekly visitors — the segments will be too small to matter.
- If an audience would be too narrow (e.g., "Chrome users on iOS from Germany with the referrer containing 'example.com'"), warn the user that the segment may be empty.
- Use `accelerate/get-audience-fields` as the source of truth for what's targetable. Don't invent fields.
