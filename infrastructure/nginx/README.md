# Infrastructure — Nginx Reverse Proxy

Production-grade Nginx configuration for CareRemind.

## Files

| File | Purpose |
|------|---------|
| `nginx.conf` | **Production** config — SSL/TLS, HSTS, rate limiting, gzip |
| `nginx.dev.conf` | **Development** config — No SSL, same routing rules |
| `Dockerfile` | Alpine-based Nginx image |

## Features

- **SSL/TLS termination** with Let's Encrypt (production)
- **Rate limiting** per endpoint:
  - Login: 5 req/s (brute-force protection)
  - General API: 30 req/s
  - Webhooks: 50 req/s (Meta sends bursts)
- **Request size limits**:
  - Default: 1MB
  - Upload endpoints: 25MB (Excel + photos)
  - Webhooks: 10MB
- **Security headers**: HSTS, X-Frame-Options DENY, X-Content-Type-Options, XSS Protection
- **Gzip compression** for JSON, CSS, JS, SVG, fonts
- **WebSocket support** for Vite HMR (dev hot-reload)
- **Static asset caching** (1 year for hashed Vite assets)

## Routing

```
/health, /health/ready  →  FastAPI (no auth, no logging)
/api/*                  →  FastAPI backend (port 8000)
/docs, /redoc           →  FastAPI Swagger UI
/api/v1/upload/*        →  FastAPI (25MB body limit, 120s timeout)
/api/v1/webhooks/*      →  FastAPI (10MB body, passes Razorpay signature header)
/*                      →  React frontend (port 3000)
```

## Usage

### Development (Docker Compose)

Add to your `docker-compose.yml`:

```yaml
nginx:
  build: ./infrastructure/nginx
  ports:
    - "80:80"
  volumes:
    - ./infrastructure/nginx/nginx.dev.conf:/etc/nginx/nginx.conf
  depends_on:
    - fastapi
    - frontend
```

### Production

```yaml
nginx:
  build: ./infrastructure/nginx
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf
    - /etc/letsencrypt/live/yourdomain.com/fullchain.pem:/etc/nginx/ssl/fullchain.pem:ro
    - /etc/letsencrypt/live/yourdomain.com/privkey.pem:/etc/nginx/ssl/privkey.pem:ro
    - certbot_webroot:/var/www/certbot
  depends_on:
    - fastapi
    - frontend
```

### SSL Certificate Setup

```bash
# Install certbot
sudo apt install certbot

# Get certificate (standalone mode before nginx is running)
sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com

# Or with running nginx (webroot mode)
sudo certbot certonly --webroot -w /var/www/certbot -d yourdomain.com
```
