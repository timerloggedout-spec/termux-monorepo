# Deploy on Vultr Cloud Compute

## One-command bootstrap

After provisioning Ubuntu 24.04, opening TCP 22/80/443, and pointing DNS to the VM, copy the app's deploy folder to the VM or run the script from a sparse checkout. Set a long random token and your domain in the shell; do not place either in source control:

    export MATCHDESK_DOMAIN=app.example.com
    export MATCHDESK_ADMIN_TOKEN='use-a-long-random-secret'
    export MATCHDESK_BRANCH=master
    sudo -E bash deploy/bootstrap-vultr.sh

The script installs Python, Git, and Caddy; checks out the selected monorepo branch; installs the systemd service; writes the token into a root-owned mode-0600 environment file; configures Caddy; and starts the app. Optional inference environment variables may be set in the shell before invoking it. The script does not provision the Vultr VM or DNS record.

This is a manual, evidence-gated deployment recipe. It does not claim that a VM, DNS name, TLS certificate, or public URL has already been created.

## Provision

Create an Ubuntu 24.04 LTS x86_64 Cloud Compute VM. For the synthetic demo, 1 vCPU / 2 GB RAM is sufficient. Allow inbound TCP 22, 80, and 443; do not expose port 8080. Point a DNS A/AAAA record at the VM.

## Install

On the VM:

    sudo apt-get update
    sudo apt-get install -y python3 git caddy
    sudo useradd --system --home /opt/match-impact-desk --shell /usr/sbin/nologin matchdesk || true
    sudo mkdir -p /opt/match-impact-desk/data
    sudo git clone --depth 1 --filter=blob:none --sparse https://github.com/timerloggedout-spec/termux-monorepo.git /tmp/termux-monorepo
    cd /tmp/termux-monorepo
    sudo git sparse-checkout set apps/match-impact-desk
    sudo cp -a apps/match-impact-desk/. /opt/match-impact-desk/
    sudo chown -R matchdesk:matchdesk /opt/match-impact-desk

The master branch is the production source after PR promotion. For a pre-merge demo, checkout the feature branch before copying the app.

## Configure

Create /etc/match-impact-desk.env with root ownership and mode 0600. Set MATCHDESK_DB=/opt/match-impact-desk/data/matchdesk.sqlite3 and a long random MATCHDESK_ADMIN_TOKEN. Optional inference settings belong in this file too. Never commit secrets.

## Start

    sudo cp /opt/match-impact-desk/deploy/match-impact-desk.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable --now match-impact-desk
    sudo cp /opt/match-impact-desk/deploy/Caddyfile /etc/caddy/Caddyfile

Replace YOUR_DOMAIN in /etc/caddy/Caddyfile with the real DNS name, then run:

    sudo caddy validate --config /etc/caddy/Caddyfile
    sudo systemctl reload caddy
    curl -fsS http://127.0.0.1:8080/health
    curl -fsS https://YOUR_DOMAIN/health

## Acceptance evidence

Do not mark deployed until VM identity/region, DNS, HTTPS, external browser access, successful authorized decision, stale-version HTTP 409, valid audit-chain result, evidence export, and clean service logs are recorded. No payment or ERP writeback should be enabled for the hackathon demo.
