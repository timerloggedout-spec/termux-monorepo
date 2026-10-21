# Render image lane (termux-readme-extractor)

The Git-backed service `termux-readme-extractor` builds with `cat README.md`. Each build still clones the full monorepo, and that clone ate the Hobby workspace's 500 included pipeline minutes. The dashboard read 500/500 on 2026-10-19.

This lane is additive:
- `ops/render-image/Dockerfile` is a busybox httpd image serving README.md (about 5 MB).
- `.github/workflows/readme-extractor-image.yml` builds it on README changes with a sparse checkout and pushes `ghcr.io/timerloggedout-spec/termux-readme-extractor:{latest,<sha7>}`.
- A separate free Render web service, image-backed, pulls that image. Render's build-pipeline docs list pipeline tasks as build command, pre-deploy command, and Dockerfile builds. Image pulls aren't among them (inferred; verified per deploy in ops/quota-state.md).

The original Git-backed service is left unchanged.
Sources: https://render.com/docs/build-pipeline, https://render.com/docs/deploying-an-image
