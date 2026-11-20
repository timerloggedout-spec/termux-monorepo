---
type: skill
name: slides-from-spec
description: Generate presentation decks from one-shot spec.json or positioning narrative
author: usman
model: sonnet
tools: Task
---

# Slides from Spec — AI-Powered Presentation Generation

Generate beautiful, full-bleed presentation decks from code generation specifications or marketing narratives.

## What This Skill Does

Takes either a **spec.json** (from `/one-shot` generation) or **positioning narrative** and generates a complete presentation deck:

1. **Input:** spec.json OR positioning brief
2. **Generation:** Node.js → Kie.ai API → PNG images
3. **Compilation:** Python → Google Slides API → PPTX file
4. **Output:** PowerPoint deck ready for presentations, demos, or internal sharing

## Two Use Cases

### Use Case 1: Demo Deck (from spec.json)

**Input:** Generated spec.json from `/one-shot "shopping cart" @./project`

**Output:** 10-15 slide deck showing:
- Slide 1: Feature title + description
- Slides 2-3: Entity relationship diagram
- Slides 4-6: Generated code samples (with syntax highlighting)
- Slide 7: Test results (✅ passing)
- Slide 8: Migration preview
- Slide 9: Integration summary
- Slide 10: Call to action ("Ready to commit?")

**Perfect for:** Sales demos, onboarding calls, internal showcases, conference talks about generated code.

### Use Case 2: Conference Talk (from positioning narrative)

**Input:** POSITIONING.md + LAUNCH_NARRATIVE.md

**Output:** 20-25 slide presentation:
- Slides 1-2: Title + speaker info
- Slides 3-5: Problem statement (why manual scaffolding sucks)
- Slides 6-8: Solution (how One-Shot works)
- Slides 9-11: Live demo (code generation in action)
- Slides 12-14: Metrics (99% accuracy, 94% test pass, etc.)
- Slides 15-17: Differentiation (vs templates, vs copilot)
- Slides 18-20: Getting started + call to action
- Slides 21-25: Q&A backup slides

**Perfect for:** Conference talks, webinars, team presentations, investor pitches.

## Invocation

### Demo Deck (from spec.json)
```
/slides-from-spec @./path-to-spec.json --style isometric --template demo-deck

Output: one-shot-demo-deck.pptx (in current directory)
```

### Conference Talk (from narrative)
```
/slides-from-spec --narrative POSITIONING.md LAUNCH_NARRATIVE.md --style ted-ed --template conference-talk

Output: one-shot-conference-talk.pptx
```

### Onboarding Deck (quickstart)
```
/slides-from-spec --template onboarding --style isometric

Output: one-shot-onboarding.pptx
```

## Style Options

### Isometric (Board Deck)
- 3D isometric illustrations
- Professional, data-heavy
- Best for: Strategy, roadmaps, technical deep-dives
- Example: Floating 3D cities, stacked blocks, gear visualizations

### TED-Ed (Story Deck)
- Warm, narrative-focused
- Hand-drawn aesthetic
- Best for: Storytelling, culture, impact
- Example: Character journeys, emotional hooks, metaphors

Both styles use full-bleed images (no text overlays except title slides).

## Behind the Scenes

1. **YAML Template** (`demo-deck.yaml`) — maps sections to Kie.ai prompts
2. **Node.js Generation** (`generate.js`) — calls Kie.ai API, saves PNGs
3. **Python Compilation** (`compile.py`) — uploads to Google Drive, builds PPTX

Each slide is a full-bleed PNG image (1920x1080) + speaker notes (as text on the slide).

## Setup

Before using this skill, you need:

1. **Kie.ai API Key** (free tier: 100 images/month)
   - Sign up: https://kie.ai
   - Create API key in dashboard
   - Set: `export KIE_API_KEY=your_key_here`

2. **Google Service Account** (free, one-time setup)
   - Go to Google Cloud Console
   - Create service account
   - Enable Google Drive + Google Slides APIs
   - Download JSON credentials file
   - Set: `export GOOGLE_CREDENTIALS_JSON=/path/to/creds.json`

3. **Dependencies**
   ```bash
   npm install kie axios dotenv  # Node.js
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pillow pptx pyyaml  # Python
   ```

## Examples

**Example 1: Generate demo deck from spec.json**
```
User: "I just generated a shopping cart feature. Can you turn the spec into a demo deck?"

/slides-from-spec @./generated/shopping-cart-spec.json --style isometric --template demo-deck

Output: shopping-cart-demo.pptx (ready for sales calls)
```

**Example 2: Generate conference talk from positioning**
```
User: "I want to give a talk on One-Shot at PyCon. Can you turn our positioning into slides?"

/slides-from-spec --narrative docs/POSITIONING.md docs/LAUNCH_NARRATIVE.md --style ted-ed --template conference-talk

Output: one-shot-pycon-talk.pptx (20 slides, ready for speaker notes)
```

**Example 3: Generate onboarding deck**
```
User: "New team members need to understand how One-Shot works. Can you create an onboarding deck?"

/slides-from-spec --template onboarding --style isometric

Output: one-shot-onboarding.pptx (5-7 slides, quickstart guide)
```

## What's Not Included

- Text overlay on images (each slide is full-bleed PNG)
- Animations or transitions (use PowerPoint manually if needed)
- Video embedding (manual step)
- Speaker timer integration (add in PowerPoint)

## Help

- Setup issues? See README.md
- API limits? Contact kie.ai support
- Google auth errors? Check GOOGLE_CREDENTIALS_JSON path
