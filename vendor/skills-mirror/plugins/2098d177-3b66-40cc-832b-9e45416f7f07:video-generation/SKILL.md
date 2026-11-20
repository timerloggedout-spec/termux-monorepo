---
name: video-generation
description: Generate video or images with ManyMotions — choosing the right model, submitting a job, and polling it to completion. Use whenever the user asks to generate, render, or create a video clip, a shot, a product image, or an AI image, and ManyMotions is connected.
---

# Generating media with ManyMotions

Generation is asynchronous and costs credits. The whole flow is three calls:
`list_models` → `media_forge_generate` → `job_status` (repeatedly).

## 1. Always call `list_models` first

Never hand-build a model id. `list_models` is free and read-only, and returns the
exact ids alongside each model's capabilities. Each video model exposes up to
three separate ids and you must pick the one matching your inputs:

| You have | Use the field | Meaning |
|---|---|---|
| A prompt only | `t2v_id` | text → video |
| A prompt + one image | `i2v_id` | image → video (image is the first frame) |
| A prompt + several reference images | `ref2v_id` | reference → video, one coherent multi-shot scene |

Image models return a `category`, supported ratios, resolutions, and `max_images`.

Passing an id that does not exist errors at submit time, so read the catalogue
rather than guessing from a model's marketing name.

## 2. Submit

```
media_forge_generate(
  type: "video" | "image",
  model_id: "<exact id from list_models>",
  params: { prompt, duration?, aspect_ratio?, image_url?, reference_urls?, count?, quality? }
)
```

Returns `{ job_id }`. Supplying `image_url` to a video model switches it to
image-to-video, so pair it with the `i2v_id`, not the `t2v_id`.

## 3. Poll

Call `job_status(job_id)` until `status` is `completed`, then read `result.video`
or `result.images`. Poll promptly and keep polling — jobs are held in memory, so
a deploy during a long gap can drop an in-flight job and return `job_not_found`.
The remedy is to resubmit.

## Writing prompts that work

- Camera movement comes from the prompt, not a parameter. Say "slow push in",
  "handheld follow", "locked-off wide" explicitly.
- Seedance 2.0 generates its own audio. If you do not want speech, say so.
- Shorter durations render faster and cost less; default to the shortest length
  that carries the shot rather than the maximum.
- One shot per generation. For a sequence, generate the shots separately and
  assemble them on a timeline — see the `video-editing` skill.

## Cost discipline

Every `media_forge_generate` call spends the user's credits, whether or not they
like the result. Before firing several generations in a row, say what you are
about to generate and roughly how many calls it will take. Do not silently loop
on regenerations to chase a better take.
