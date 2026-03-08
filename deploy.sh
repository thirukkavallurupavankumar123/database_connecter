#!/bin/bash
# ═══════════════════════════════════════════════════════════
# ARGO Analytics — Server Deployment Script
# Run on a fresh Ubuntu 22.04+ server
# Usage: chmod +x deploy.sh && sudo ./deploy.sh
# ═══════════════════════════════════════════════════════════
set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   ARGO Analytics — Server Deployment         ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── Step 1: Install Docker if not present ──────────────────
if ! command -v docker &> /dev/null; then
    echo "[1/5] Installing Docker..."
    apt-get update -y
    apt-get install -y ca-certificates curl gnupg
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl enable docker
    systemctl start docker
    echo "  ✅ Docker installed"
else
    echo "[1/5] Docker already installed"
fi

# ── Step 2: Check .env file ───────────────────────────────
echo ""
if [ ! -f .env ]; then
    echo "[2/5] Creating .env from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo ""
        echo "  ⚠️  IMPORTANT: Edit .env with your actual values:"
        echo "     nano .env"
        echo ""
        echo "  Required keys:"
        echo "    - GROQ_API_KEY      (get from console.groq.com)"
        echo "    - ENCRYPTION_KEY    (auto-set below)"
        echo "    - POSTGRES_PASSWORD (change from default!)"
        echo ""
    else
        cat > .env << 'ENVFILE'
GROQ_API_KEY=your_groq_api_key_here
ENCRYPTION_KEY=change_me
POSTGRES_USER=argo_user
POSTGRES_PASSWORD=argo_pass
POSTGRES_DB=argo_db
FRONTEND_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
ENVFILE
        echo "  ⚠️  Created .env — edit it with your API keys: nano .env"
    fi
else
    echo "[2/5] .env file found"
fi

# ── Step 3: Generate encryption key if needed ──────────────
echo ""
echo "[3/5] Checking encryption key..."
if grep -q "change_me\|your_fernet" .env 2>/dev/null; then
    NEW_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || echo "")
    if [ -n "$NEW_KEY" ]; then
        sed -i "s|ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$NEW_KEY|g" .env
        echo "  ✅ Generated new encryption key"
    else
        echo "  ⚠️  Could not auto-generate key. Set ENCRYPTION_KEY in .env manually."
    fi
else
    echo "  ✅ Encryption key already set"
fi

# ── Step 4: Build and start services ──────────────────────
echo ""
echo "[4/5] Building and starting services..."
docker compose down --remove-orphans 2>/dev/null || true
docker compose build --no-cache
docker compose up -d

# ── Step 5: Verify ────────────────────────────────────────
echo ""
echo "[5/5] Verifying deployment..."
sleep 10

# Check containers
echo ""
echo "Container status:"
docker compose ps

# Health check
echo ""
BACKEND_OK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs 2>/dev/null || echo "000")
FRONTEND_OK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")

if [ "$BACKEND_OK" = "200" ]; then
    echo "  ✅ Backend API:  http://$(hostname -I | awk '{print $1}'):8000"
else
    echo "  ⏳ Backend starting... (check: docker compose logs backend)"
fi

if [ "$FRONTEND_OK" = "200" ]; then
    echo "  ✅ Frontend UI:  http://$(hostname -I | awk '{print $1}'):3000"
else
    echo "  ⏳ Frontend starting... (check: docker compose logs frontend)"
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "  PostgreSQL: localhost:5432 (argo_db)"
echo "  Backend:    http://localhost:8000"
echo "  Frontend:   http://localhost:3000"
echo "  API Docs:   http://localhost:8000/docs"
echo "═══════════════════════════════════════════════"
echo ""
echo "Useful commands:"
echo "  docker compose logs -f        # View all logs"
echo "  docker compose logs backend   # Backend logs only"
echo "  docker compose restart        # Restart all"
echo "  docker compose down           # Stop all"
echo "  docker compose up -d          # Start all"
echo ""
