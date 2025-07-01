# Poker-AI Backend HTTPS / SSL Setup

This document captures the **working** production setup that serves the Poker-AI backend securely over HTTPS while keeping the Flask–SocketIO server running in plain HTTP mode.

---

## Architecture Overview

```
Browser ── HTTPS ──▶ Nginx (port 5001, TLS termination)
                         │
                         └── HTTP ──▶ Flask-SocketIO backend (127.0.0.1:5101)
```

* Nginx terminates TLS on `aico-music.com:5001` using Let’s Encrypt certificates located in `/etc/letsencrypt/live/aico-music.com/`.
* The backend process listens **without SSL** on the internal port **5101**.  Only Nginx can reach this port.
* Web-socket upgrades (`/socket.io/`) and normal REST endpoints (`/`) are proxied through the same server block.

---

## Backend Service

Run the backend with the port set to `5101`:

```bash
PORT=5101 python3 /home/ec2-user/poker_ai/poker_ai/web/backend/app.py
```

The code already falls back to HTTP when certificates are not readable, so no changes to `app.py` are required.

---

## Nginx Configuration Snippet

The following block was appended **inside the `http {}` section** of `/etc/nginx/nginx.conf` (the conf.d include was disabled, so we embedded it directly):

```nginx
# === Poker-AI backend HTTPS on 5001 ===
server {
    listen 5001 ssl;
    listen [::]:5001 ssl;
    server_name aico-music.com;

    ssl_certificate     /etc/letsencrypt/live/aico-music.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aico-music.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers   HIGH:!aNULL:!MD5;

    # REST + long-polling endpoints
    location / {
        proxy_pass http://127.0.0.1:5101;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }

    # WebSocket upgrades for Socket.IO
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5101;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
# === end Poker-AI block ===
```

Apply the config:

```bash
sudo nginx -t   # syntax check
sudo systemctl reload nginx
```

---

## Certificate Renewal

This setup continues to use the existing Let’s Encrypt certificates managed by Certbot.  After renewal (usually via systemd timer or cron), reload Nginx to pick up the new cert:

```bash
sudo systemctl reload nginx
```

---

## Quick Validation Commands

```bash
# Backend (plain HTTP)
curl http://127.0.0.1:5101/health

# Through Nginx (TLS)
curl -k https://aico-music.com:5001/health

# Create new game
curl -k -X POST https://aico-music.com:5001/game/new -H "Content-Type: application/json" -d '{"num_ai_players":2}'
```

---

## Troubleshooting Tips

1. **Port Clash** – ensure **nothing else** is listening on 5001 before reloading Nginx.
2. **Nginx not listening** – confirm the server block is inside the `http {}` section and Nginx passed `nginx -t`.
3. **WebSocket errors** – check that the `/socket.io/` location contains the `Upgrade` and `Connection` headers.

---

_Last updated: 2025-07-01_
