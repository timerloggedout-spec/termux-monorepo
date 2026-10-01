FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl ca-certificates build-essential python3 python3-pip python3-venv \
      git jq unzip libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# uv via pip (avoids curl-installer quirks)
RUN pip3 install --no-cache-dir uv

USER vscode
