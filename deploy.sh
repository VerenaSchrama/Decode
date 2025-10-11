#!/bin/bash
set -e

echo "🚀 Deploying backend to Hetzner..."

# Change this to your server IP (or SSH alias if configured)
SERVER="root@65.108.149.135"
APP_DIR="/srv/mybackend"

# 1️⃣ Sync only the backend folder to the server
rsync -avz --exclude '__pycache__' --exclude 'venv' \
  ./backend/ ${SERVER}:${APP_DIR}

# 2️⃣ Restart backend service via systemd
ssh ${SERVER} "systemctl restart mybackend && systemctl status mybackend --no-pager"

#3. restart backend server
ssh ${SERVER} "systemctl restart mybackend && systemctl status mybackend --no-pager"

echo "✅ Deployment complete!"

