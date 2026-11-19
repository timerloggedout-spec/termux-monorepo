---
description: "Save an AnimatedWebs template, component or background to your favourites, or list what you saved"
argument-hint: "[name or slug to save; leave empty to list your saved items]"
---

If "$ARGUMENTS" is empty, call `save_item` with action `list` and show the saved templates, components and backgrounds in a short table with their links.

Otherwise find "$ARGUMENTS" with `search_catalog`, confirm the match when more than one item fits, and call `save_item` with action `save`, the matching type (`template`, `component` or `background`) and the item's slug or id. To remove a favourite, use action `unsave`. Saved templates are the same list as the Save heart on animatedwebs.com.
