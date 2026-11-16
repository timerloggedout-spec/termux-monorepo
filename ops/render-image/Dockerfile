# Tiny image-backed lane for Render service termux-readme-extractor.
# Built in GitHub Actions (free for this public repo) so Render only PULLS:
# image deploys run no build command, so they should use no Render pipeline minutes.
FROM --platform=linux/amd64 busybox:1.36-musl
COPY README.md /www/README.md
RUN printf '<!doctype html><meta charset="utf-8"><title>termux-readme-extractor</title><a href="README.md">README.md</a>\n' > /www/index.html
ENV PORT=10000
EXPOSE 10000
CMD ["sh", "-c", "exec httpd -f -v -p 0.0.0.0:${PORT} -h /www"]
