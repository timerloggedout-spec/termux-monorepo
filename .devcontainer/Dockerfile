# Session 143 · deterministic Docker-in-Docker for Codespaces
# Base: Ubuntu (devcontainers/base:ubuntu). No feature flags.
FROM mcr.microsoft.com/devcontainers/base:ubuntu

USER root

# Core prereqs for docker repo
RUN apt-get update && apt-get install -y --no-install-recommends \
      apt-transport-https \
      ca-certificates \
      curl \
      gnupg \
      lsb-release \
      sudo \
      python3 \
      python3-pip \
      python3-venv \
      git \
      jq \
      unzip \
 && rm -rf /var/lib/apt/lists/*

# Docker CE from official repo
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
      | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
      > /etc/apt/sources.list.d/docker.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      docker-ce \
      docker-ce-cli \
      containerd.io \
      docker-buildx-plugin \
      docker-compose-plugin \
 && rm -rf /var/lib/apt/lists/*

# Non-root docker for vscode user
RUN usermod -aG docker vscode 2>/dev/null || true

# dind init script for daemon startup
RUN curl -fsSL https://raw.githubusercontent.com/devcontainers/features/main/src/docker-in-docker/scripts/docker-init.sh \
      -o /usr/local/share/docker-init.sh \
 && chmod +x /usr/local/share/docker-init.sh

USER vscode
