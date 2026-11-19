---
description: Show a ManyMotions project's timeline and take an editing instruction
---

Work on a ManyMotions video timeline: $ARGUMENTS

1. If no project is named, call `video_editor_list_projects` and ask which one.
2. Call `video_editor_get_timeline` and show the current layout — every clip in
   order with its duration and running start time. Both calls are free.
3. Carry out the requested edit with the deterministic tools where possible
   (`add_clip`, `remove_clip`, `reorder_clip`, `set_transition`,
   `upload_captions`). These cost no credits.
4. Only fall back to `video_editor_instruct` for creative work that needs
   generation — and say so first, because it spends credits.
5. Export with `video_editor_export` when the user asks for the final file.
