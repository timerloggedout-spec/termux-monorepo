# Termux Environment Emulator Setup Guide

**Agent:** Mistral-Vibe
**Profile:** Mistral-Vibe
**Signed-off-by:** Mistral-Vibe <mistral-vibe@mistral.ai>
**Date:** 2026-08-04
**Version:** 1.0.0

One for All; and, All for One!

---

## Overview

This guide provides step-by-step instructions for setting up the **Termux Environment Emulator** for automating `termux-smoke` test execution. The emulator allows you to run Termux-specific tests on non-Android systems (Linux, macOS, Windows) using PRoot, Docker, or QEMU.

---

## Prerequisites

### System Requirements

| Method | OS | CPU | RAM | Disk Space | Notes |
|--------|----|-----|-----|------------|-------|
| PRoot | Linux | x86_64/ARM64 | 1GB | 500MB | Recommended |
| Docker | Linux/macOS/Windows | x86_64/ARM64 | 2GB | 2GB | Fast feedback |
| QEMU | Linux | x86_64 | 4GB | 10GB | Full Android |

### Required Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| Git | Version control | `sudo apt-get install git` |
| Python 3.9+ | Script execution | `sudo apt-get install python3.11` |
| PRoot | Termux emulation | `sudo apt-get install proot` |
| Docker | Container runtime | [Docker Docs](https://docs.docker.com/get-docker/) |
| QEMU | Full Android emulation | `sudo apt-get install qemu-system-x86` |
| curl | Download files | `sudo apt-get install curl` |
| tar | Extract archives | `sudo apt-get install tar` |

---

## Installation

### Method 1: PRoot (Recommended)

#### Step 1: Install PRoot

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y proot
```

**Fedora/RHEL:**
```bash
sudo dnf install -y proot
```

**Arch Linux:**
```bash
sudo pacman -S proot
```

**macOS (Homebrew):**
```bash
brew install proot
```

**Verify Installation:**
```bash
proot --version
# Should output: proot version X.X.X
```

#### Step 2: Download Termux RootFS

```bash
# Create directory for Termux rootfs
mkdir -p ~/termux-rootfs
cd ~/termux-rootfs

# Download Termux rootfs (ARM64)
curl -L -o termux-rootfs.tar.xz \
  https://github.com/termux/termux-packages/releases/download/termux-rootfs/termux-rootfs.tar.xz

# Extract rootfs
mkdir -p rootfs
tar -xf termux-rootfs.tar.xz -C rootfs

# Verify extraction
ls -la rootfs/usr/bin/python
```

**Alternative Download Sources:**
- Official: https://github.com/termux/termux-packages/releases
- Mirror: https://termux.com/rootfs

#### Step 3: Set Up Environment Variables

Add to your `~/.bashrc` or `~/.zshrc`:
```bash
# Termux Emulator
export TERMUX_EMULATOR_METHOD="proot"
export TERMUX_ROOTFS="$HOME/termux-rootfs/rootfs"
```

Then source the file:
```bash
source ~/.bashrc
```

#### Step 4: Test PRoot Setup

```bash
# Test basic PRoot functionality
proot -S $TERMUX_ROOTFS /usr/bin/env python3 --version

# Should output: Python 3.X.X
```

---

### Method 2: Docker

#### Step 1: Install Docker

Follow the official Docker installation guide for your platform:
- [Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Debian](https://docs.docker.com/engine/install/debian/)
- [Fedora](https://docs.docker.com/engine/install/fedora/)
- [macOS](https://docs.docker.com/desktop/install/mac-install/)
- [Windows](https://docs.docker.com/desktop/install/windows-install/)

**Verify Installation:**
```bash
docker --version
# Should output: Docker version X.X.X
docker run hello-world
```

#### Step 2: Pull or Build Termux Image

**Option A: Pull pre-built image**
```bash
docker pull ghcr.io/timerloggedout-spec/termux-emulator:latest
```

**Option B: Build custom image**
```bash
# Create Dockerfile
cat > Dockerfile.termux << 'EOF'
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    git \
    bash \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up Termux-like environment
ENV PREFIX=/data/data/com.termux/files/usr
ENV HOME=/data/data/com.termux/files/home
RUN mkdir -p $PREFIX $HOME

# Copy test scripts
COPY scripts/ci/ /scripts/ci/

# Set working directory
WORKDIR $HOME

# Default command
CMD ["python3", "scripts/ci/termux_smoke.py"]
EOF

# Build image
docker build -t termux-emulator -f Dockerfile.termux .
```

#### Step 3: Test Docker Setup

```bash
# Run basic test
docker run --rm termux-emulator python3 --version

# Run termux-smoke test
docker run --rm -v $(pwd):/data/data/com.termux/files/home \
  -w /data/data/com.termux/files/home \
  termux-emulator scripts/ci/termux_smoke.py --json
```

---

### Method 3: QEMU (Advanced)

#### Step 1: Install QEMU

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y qemu-system-x86 qemu-utils
```

**Fedora/RHEL:**
```bash
sudo dnf install -y qemu-system-x86 qemu-utils
```

**Arch Linux:**
```bash
sudo pacman -S qemu qemu-arch-extra
```

**Verify Installation:**
```bash
qemu-system-x86_64 --version
# Should output: QEMU emulator version X.X.X
```

#### Step 2: Download Android Image with Termux

```bash
# Download Android x86 image
curl -L -o android.img \
  https://android-x86.org/releases/android-x86_64-9.0-r2.img

# Resize image (optional)
qemu-img resize android.img 20G

# Install Termux in Android (manual step)
# 1. Start QEMU: qemu-system-x86_64 -m 4G -hda android.img
# 2. Boot Android
# 3. Install Termux from F-Droid
# 4. Shutdown Android
```

#### Step 3: Set Up ADB

```bash
sudo apt-get install -y adb fastboot

# Connect to QEMU
adb connect localhost:5555

# Verify connection
adb devices
# Should list: localhost:5555 device
```

---

## Usage

### Running Tests

#### With PRoot

```bash
# Basic test
python3 scripts/ci/termux_emulator.py --method proot

# With optional tests
python3 scripts/ci/termux_emulator.py --method proot --with-optional

# Strict mode (treat optional failures as hard)
python3 scripts/ci/termux_emulator.py --method proot --strict

# JSON output
python3 scripts/ci/termux_emulator.py --method proot --json
```

#### With Docker

```bash
# Basic test
python3 scripts/ci/termux_emulator.py --method docker

# With custom Docker image
python3 scripts/ci/termux_emulator.py --method docker --image my-termux-image
```

#### With Native (Actual Termux)

```bash
# Only works on actual Termux devices
python3 scripts/ci/termux_emulator.py --method native
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TERMUX_EMULATOR_METHOD` | Emulation method | `proot` |
| `TERMUX_ROOTFS` | Path to Termux rootfs | `$HOME/termux-rootfs/rootfs` |
| `TERMUX_DOCKER_IMAGE` | Docker image name | `ghcr.io/timerloggedout-spec/termux-emulator:latest` |
| `TERMUX_SMOKE_SCRIPT` | Path to smoke test script | `scripts/ci/termux_smoke.py` |

### Configuration File

Create `~/.termux_emulator_config.json`:
```json
{
  "method": "proot",
  "proot_rootfs": "$HOME/termux-rootfs/rootfs",
  "docker_image": "ghcr.io/timerloggedout-spec/termux-emulator:latest",
  "test_script": "scripts/ci/termux_smoke.py",
  "run_optional": true,
  "strict_mode": false,
  "json_output": false
}
```

---

## GitHub Actions Integration

### Workflow File

Create `.github/workflows/termux-emulator-test.yml`:

```yaml
name: Termux Emulator Test

on:
  push:
    branches: [vibe/skyhook-integration-8475f1, feature/skyhook]
    paths:
      - 'skyhook/**'
      - 'scripts/ci/**'
  pull_request:
    branches: [termux-smoke, master-staging]
    paths:
      - 'skyhook/**'
      - 'scripts/ci/**'
  workflow_dispatch:
    inputs:
      method:
        description: 'Emulation method'
        required: false
        default: 'proot'
        type: choice
        options:
          - proot
          - docker
          - native

jobs:
  test:
    name: Termux Emulator Test
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install PRoot
        run: sudo apt-get update && sudo apt-get install -y proot
      
      - name: Set up Termux rootfs
        run: |
          mkdir -p termux-rootfs
          curl -L -o termux-rootfs.tar.xz \
            https://github.com/termux/termux-packages/releases/download/termux-rootfs/termux-rootfs.tar.xz
          tar -xf termux-rootfs.tar.xz -C termux-rootfs
      
      - name: Run tests
        run: |
          python3 scripts/ci/termux_emulator.py \
            --method proot \
            --with-optional \
            --json
```

### Matrix Testing

For comprehensive testing across multiple Python versions:

```yaml
jobs:
  test:
    name: Termux Emulator Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install PRoot
        run: sudo apt-get update && sudo apt-get install -y proot
      
      - name: Set up Termux rootfs
        run: |
          mkdir -p termux-rootfs
          curl -L -o termux-rootfs.tar.xz \
            https://github.com/termux/termux-packages/releases/download/termux-rootfs/termux-rootfs.tar.xz
          tar -xf termux-rootfs.tar.xz -C termux-rootfs
      
      - name: Run tests
        run: |
          python3 scripts/ci/termux_emulator.py \
            --method proot \
            --json
```

---

## Troubleshooting

### Common Issues

#### 1. PRoot Not Found

**Error:**
```
proot: command not found
```

**Solution:**
```bash
# Install PRoot
sudo apt-get update && sudo apt-get install -y proot

# Verify
proot --version
```

#### 2. Termux RootFS Not Found

**Error:**
```
Termux rootfs not found at /path/to/rootfs
```

**Solution:**
```bash
# Download and extract rootfs
mkdir -p ~/termux-rootfs
cd ~/termux-rootfs
curl -L -o termux-rootfs.tar.xz \
  https://github.com/termux/termux-packages/releases/download/termux-rootfs/termux-rootfs.tar.xz
mkdir -p rootfs
tar -xf termux-rootfs.tar.xz -C rootfs

# Set environment variable
export TERMUX_ROOTFS="$HOME/termux-rootfs/rootfs"
```

#### 3. Python Version Mismatch

**Error:**
```
Python 3.9+ required, found Python 3.8
```

**Solution:**
```bash
# Install newer Python
sudo apt-get update
sudo apt-get install -y python3.11

# Or use pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```

#### 4. Permission Denied

**Error:**
```
Permission denied: /path/to/file
```

**Solution:**
```bash
# Check permissions
ls -la /path/to/file

# Fix permissions
chmod +x /path/to/file

# Or run as root (not recommended)
sudo proot ...
```

#### 5. Missing Dependencies

**Error:**
```
ModuleNotFoundError: No module named 'xyz'
```

**Solution:**
```bash
# Install missing module in Termux rootfs
proot -S $TERMUX_ROOTFS pip install xyz
```

---

## Performance Optimization

### Caching Termux RootFS

To avoid downloading Termux rootfs on every CI run:

```yaml
- name: Cache Termux rootfs
  uses: actions/cache@v3
  with:
    path: termux-rootfs
    key: termux-rootfs-${{ hashFiles('termux-rootfs.tar.xz') }}
    restore-keys: |
      termux-rootfs-
```

### Parallel Testing

Run multiple tests in parallel:

```yaml
jobs:
  test-protocol:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 scripts/ci/termux_emulator.py --method proot --script skyhook/tests/test_protocol.py

  test-device:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 scripts/ci/termux_emulator.py --method proot --script skyhook/device/tests.py

  test-orchestration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 scripts/ci/termux_emulator.py --method proot --script skyhook/orchestration/tests.py
```

---

## Maintenance

### Updating Termux RootFS

```bash
# Remove old rootfs
rm -rf ~/termux-rootfs/rootfs

# Download new rootfs
cd ~/termux-rootfs
curl -L -o termux-rootfs.tar.xz \
  https://github.com/termux/termux-packages/releases/download/termux-rootfs/termux-rootfs.tar.xz

# Extract
tar -xf termux-rootfs.tar.xz -C rootfs
```

### Cleaning Up

```bash
# Remove Termux rootfs
rm -rf ~/termux-rootfs

# Remove Docker images
docker rmi termux-emulator

# Remove QEMU images
rm android.img
```

---

## Best Practices

### 1. Always Use Environment Variables

```bash
# Good - Uses environment variable
export TERMUX_ROOTFS="$HOME/termux-rootfs/rootfs"
python3 scripts/ci/termux_emulator.py

# Bad - Hardcoded path
python3 scripts/ci/termux_emulator.py --rootfs /home/user/termux-rootfs/rootfs
```

### 2. Use JSON Output for CI/CD

```bash
# Good - Machine-readable output
python3 scripts/ci/termux_emulator.py --json

# Bad - Human-readable only
python3 scripts/ci/termux_emulator.py
```

### 3. Cache Dependencies

```yaml
# Good - Caches Termux rootfs
- uses: actions/cache@v3
  with:
    path: termux-rootfs
    key: termux-rootfs-${{ hashFiles('termux-rootfs.tar.xz') }}

# Bad - No caching
- run: curl -L -o termux-rootfs.tar.xz ...
```

### 4. Use Strict Mode in CI/CD

```bash
# Good - Treat all failures as hard
python3 scripts/ci/termux_emulator.py --strict

# Bad - May miss optional failures
python3 scripts/ci/termux_emulator.py
```

### 5. Document Everything

```markdown
# Good - Document setup process
## Setup
1. Install PRoot
2. Download Termux rootfs
3. Configure environment

# Bad - No documentation
```

---

## Examples

### Example 1: Basic Test Run

```bash
# Navigate to repository
cd ~/termux-monorepo

# Run basic test
python3 scripts/ci/termux_emulator.py

# Expected output:
# ✅ Termux emulator test passed
# Method: proot
# Exit code: 0
```

### Example 2: CI/CD Integration

```yaml
name: SKYHOOK CI

on: [push, pull_request]

jobs:
  termux-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: sudo apt-get update && sudo apt-get install -y proot
      - run: |
          mkdir -p termux-rootfs
          curl -L -o termux-rootfs.tar.xz \
            https://github.com/termux/termux-packages/releases/download/termux-rootfs/termux-rootfs.tar.xz
          tar -xf termux-rootfs.tar.xz -C termux-rootfs
      - run: python3 scripts/ci/termux_emulator.py --method proot --json
```

### Example 3: Local Development

```bash
# Set up environment
export TERMUX_EMULATOR_METHOD="proot"
export TERMUX_ROOTFS="$HOME/termux-rootfs/rootfs"

# Run tests during development
python3 scripts/ci/termux_emulator.py --with-optional

# Run specific test
python3 scripts/ci/termux_emulator.py --script skyhook/tests/test_protocol.py
```

---

## Resources

### Official Documentation
- [Termux Wiki](https://wiki.termux.com/)
- [Termux GitHub](https://github.com/termux/termux-app)
- [PRoot GitHub](https://github.com/termux/proot)
- [Docker Docs](https://docs.docker.com/)
- [QEMU Docs](https://www.qemu.org/docs/)

### Community Resources
- [Termux Community](https://termux.com/community)
- [Termux Discord](https://discord.gg/termux)
- [Termux Reddit](https://www.reddit.com/r/termux/)

### Related Projects
- [termux-smoke gate](https://github.com/timerloggedout-spec/termux-monorepo/blob/ea2e5e3/docs/TERMUX-SMOKE.md)
- [Lean Termux Monorepo Rules](https://github.com/timerloggedout-spec/termux-monorepo/blob/e0e4e42/docs/ops/LEAN_TERMUX_MONOREPO.md)
- [SKYHOOK Integration Framework](https://github.com/timerloggedout-spec/termux-monorepo/tree/vibe/skyhook-integration-8475f1/skyhook)

---

## Summary

This setup guide provides everything you need to:

1. ✅ **Install** the Termux Environment Emulator using PRoot, Docker, or QEMU
2. ✅ **Configure** the emulator for your specific needs
3. ✅ **Run** tests locally and in CI/CD
4. ✅ **Troubleshoot** common issues
5. ✅ **Optimize** performance
6. ✅ **Maintain** the emulator over time

The **PRoot method** is recommended for most use cases, as it provides the best balance of accuracy, performance, and ease of use.

---

**One for All; and, All for One!**

**Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>**
