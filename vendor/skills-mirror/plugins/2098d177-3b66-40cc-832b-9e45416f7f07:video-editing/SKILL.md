---
name: video-editing
description: Assemble a finished video on ManyMotions's multi-track timeline — projects, clips, trims, transitions, captions and MP4 export. Use whenever the user wants to cut, arrange, sequence, subtitle, or export a video rather than generate a single clip.
---

# Editing on the ManyMotions timeline

A **project** holds N **videos** that all share one media **library**. Each video
has its own multi-track timeline (video / voice / sfx / music) and its own chat
thread with the editor agent.

## The loop

1. `video_editor_create_project(name, aspect_ratio)` → `project_id`
2. Fill the library — `video_editor_add_reference(url)` for anything already
   online, `video_editor_upload_file` for small local files, or generate new
   assets (see the `video-generation` skill).
3. `video_editor_add_clip(project_id, asset_id, track?, position?)` for each
   placement. Prefer this over asking `video_editor_instruct` to "add a clip" —
   it is deterministic and free.
4. `video_editor_export(project_id, video_id?)` → `video_url`.

## Read the timeline before you change it

`video_editor_get_state` returns structure and ids only. It does **not** include
durations. To see the actual layout — every clip in playback order with
`clip_id`, `duration_sec`, cumulative `timeline_start_sec`, trims, speeds,
volumes and captions — call `video_editor_get_timeline`. It is free and
read-only. Do this before any reorder, trim or transition, and reference clips by
`clip_id` afterwards.

## Deterministic ops vs the agent

These cost nothing and do exactly what they say — reach for them first:

`add_clip`, `remove_clip`, `reorder_clip`, `set_transition`, `upload_captions`,
`export_captions`, `add_reference`, and the whole `get_*` / `list_*` family.

`video_editor_instruct` hands one instruction to the editor agent, which may
generate media and therefore **spend credits**. Use it for creative work you
cannot express as a direct call, not for mechanical timeline edits.

## Uploading files

Under ~6 MB: `video_editor_upload_file` with base64 bytes. Anything larger will
fail with a parse error — use `video_editor_request_upload` instead, PUT the raw
bytes to the returned `upload_url`, then register the `file_url` with
`video_editor_add_reference`.

## Captions

`video_editor_upload_captions` takes inline SRT or VTT and burns in on export.
Three render modes: `static` (one line per cue), `wordpop` (one word at a time,
TikTok style), `karaoke` (highlight sweeps the line). Styles include `tiktok`,
`classic`, `bold`, `minimal`. Set `y_pct` around 65 to keep text clear of
platform UI. It **replaces** existing captions unless you pass `append: true`.

## Persistent direction

`video_editor_set_context` stores a brief the editor agent re-reads every turn —
style, characters, do's and don'ts. Set it once at project level rather than
repeating the same direction in every instruction. Pass `append: true` to add to
it; the default replaces it.

## Images on the video track

An image placed on the video track is held as a still for `duration_sec`
(default 1s), like a slideshow frame. That is the way to build a stills sequence.
