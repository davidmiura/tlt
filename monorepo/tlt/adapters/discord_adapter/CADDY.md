# Caddy

  Two Solutions:

  Solution 1: Run Caddy on Standard Ports (Recommended)

  Update your port forwarding to:
  Port 80 → 192.168.0.254:80   ✅ (HTTP to Caddy)
  Port 443 → 192.168.0.254:443 ✅ (HTTPS to Caddy)

  Then run Caddy with sudo to bind to ports 80/443:
  # Start Discord Adapter first
  poetry run python start_discord_simple.py

  # Start Caddy on standard ports (requires sudo)
  sudo caddy run --config adapters/discord_adapter/Caddyfile.simple --adapter caddyfile

  Solution 2: Use High Ports (No sudo required)

  Update your port forwarding to:
  Port 80 → 192.168.0.254:8080   ✅ (HTTP to Caddy)
  Port 443 → 192.168.0.254:8443  ✅ (HTTPS to Caddy)

⏺ Write(adapters/discord_adapter/Caddyfile.highports)
  ⎿  Wrote 21 lines to adapters/discord_adapter/Caddyfile.highports
     {
         # Global options
         admin off
         email your_email
         # Use high ports (no sudo required)
         http_port 8080
         https_port 8443
     }
     … +11 lines (ctrl+r to expand)

⏺ 🎯 Recommended Steps:

  Step 1: Update Router Port Forwarding

  Choose one of these configurations:

  Option A (Standard ports - requires sudo):
  Port 80 → 192.168.0.254:80
  Port 443 → 192.168.0.254:443

  Option B (High ports - no sudo):
  Port 80 → 192.168.0.254:8080
  Port 443 → 192.168.0.254:8443

  Step 2: Start Services

  For Option A:
  # Terminal 1: Discord Adapter
  poetry run python start_discord_simple.py

  # Terminal 2: Caddy (standard ports)
  sudo caddy run --config adapters/discord_adapter/Caddyfile.simple --adapter caddyfile

  For Option B:
  # Terminal 1: Discord Adapter  
  poetry run python start_discord_simple.py

  # Terminal 2: Caddy (high ports)
  caddy run --config adapters/discord_adapter/Caddyfile.highports --adapter caddyfile

  Step 3: Test

  # Test HTTPS
  curl -I https://your_sub_domain.duckdns.org/health

  # Test HTTP redirect
  curl -I http://your_sub_domain.duckdns.org/health

  The key fix is ensuring your port forwarding sends HTTP/HTTPS traffic to Caddy (which handles TLS), not directly to your Discord app (which only speaks HTTP).

poetry run python run_discord_adapter.py
sudo caddy run --config adapters/discord_adapter/Caddyfile.highports --adapter caddyfile
https://your_sub_domain.duckdns.org/docs#/

```bash
cd monorepo
sudo caddy run --config tlt/adapters/discord_adapter/Caddyfile.highports --adapter caddyfile
```

```bash
cd monorepo
ENV=production poetry run python run_discord_adapter.py 
```
