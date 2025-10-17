# Deployment Guide

## Prerequisites

### Required Software
- Docker & Docker Compose (for containerized deployment)
- PostgreSQL 16+ (if running natively)
- Neo4j 5.16+ Community Edition (if running natively)
- Node.js 20+ (for frontend)
- Python 3.12+ with uv (for backend)

### Required Accounts
- Domain name (for production)
- SSL/TLS certificate provider (Let's Encrypt recommended)
- Optional: Cloud provider account (AWS, GCP, DigitalOcean, etc.)

---

## Environment Setup

### 1. Backend Environment Variables

Copy the example file and configure:

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your production values:

```bash
# Generate strong SECRET_KEY
openssl rand -hex 32

# Configure database
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/inheritance_db"

# Configure Neo4j
NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="your-strong-password"

# Set production SECRET_KEY
SECRET_KEY="your-generated-secret-key-from-openssl"

# Configure CORS for your domain
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

### 2. Frontend Environment Variables

```bash
cd frontend
cp .env.example .env.production
```

Edit `.env.production`:

```bash
NEXT_PUBLIC_API_URL="https://api.yourdomain.com"
```

---

## Deployment Options

### Option 1: Docker Compose (Recommended for Quick Start)

#### Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Production

1. **Configure environment variables**:

```bash
# Create .env file in project root
cat > .env <<EOF
POSTGRES_DB=inheritance_db
POSTGRES_USER=inheritance_user
POSTGRES_PASSWORD=$(openssl rand -hex 32)
NEO4J_USER=neo4j
NEO4J_PASSWORD=$(openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=https://yourdomain.com
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
EOF
```

2. **Start production services**:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Run database migrations**:

```bash
docker exec -it inheritance-backend-prod uv run alembic upgrade head
```

4. **Verify health checks**:

```bash
# Backend health
curl http://localhost:8000/health/ready

# Frontend health
curl http://localhost:3000
```

### Option 2: VPS Deployment (DigitalOcean, Linode, Vultr)

#### Server Setup

1. **Create server**:
   - Ubuntu 22.04 LTS
   - Minimum 2GB RAM, 2 vCPUs
   - 50GB storage

2. **Install Docker**:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

3. **Clone repository**:

```bash
git clone https://github.com/yourusername/inheritance-calculator-web.git
cd inheritance-calculator-web
```

4. **Configure environment** (see above)

5. **Setup reverse proxy with Nginx**:

Create `/etc/nginx/sites-available/inheritance-calculator`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

6. **Enable SSL with Let's Encrypt**:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

7. **Start services**:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Option 3: PaaS Deployment (Render, Railway, Fly.io)

#### Render

1. **Create PostgreSQL database**:
   - Go to Render dashboard
   - Create PostgreSQL database
   - Note the internal database URL

2. **Create Neo4j service**:
   - Deploy Neo4j Community Edition as Docker service
   - Note the connection URL

3. **Deploy Backend**:
   - Create Web Service from Git
   - Select `backend` directory
   - Build command: `uv sync && uv run alembic upgrade head`
   - Start command: `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Set environment variables from `.env.example`

4. **Deploy Frontend**:
   - Create Static Site from Git
   - Select `frontend` directory
   - Build command: `npm install && npm run build`
   - Environment variables: `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`

---

## Database Migrations

### Initial Setup

```bash
# Backend container
docker exec -it inheritance-backend-prod /bin/sh

# Run migrations
uv run alembic upgrade head

# Create initial admin user (optional)
uv run python scripts/create_admin.py
```

### Creating New Migrations

```bash
cd backend

# Auto-generate migration from model changes
uv run alembic revision --autogenerate -m "Add new feature"

# Review generated migration in alembic/versions/

# Apply migration
uv run alembic upgrade head
```

### Rollback

```bash
# Rollback one migration
uv run alembic downgrade -1

# Rollback to specific version
uv run alembic downgrade <revision_id>

# View migration history
uv run alembic history
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Basic liveness
curl http://localhost:8000/health

# Detailed readiness (checks DB connections)
curl http://localhost:8000/health/ready

# Frontend health
curl http://localhost:3000
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Backups

#### PostgreSQL Backup

```bash
# Backup
docker exec inheritance-postgres-prod pg_dump -U inheritance_user inheritance_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker exec -i inheritance-postgres-prod psql -U inheritance_user inheritance_db < backup_20250101_120000.sql
```

#### Neo4j Backup

```bash
# Backup
docker exec inheritance-neo4j-prod neo4j-admin database dump neo4j --to-path=/backups

# Copy from container
docker cp inheritance-neo4j-prod:/backups/neo4j.dump ./neo4j_backup_$(date +%Y%m%d).dump

# Restore
docker exec inheritance-neo4j-prod neo4j-admin database load neo4j --from-path=/backups/neo4j.dump
```

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run new migrations
docker exec -it inheritance-backend-prod uv run alembic upgrade head
```

---

## Security Checklist

### Pre-Production

- [ ] Change all default passwords
- [ ] Generate strong `SECRET_KEY` with `openssl rand -hex 32`
- [ ] Configure CORS to only allow your domain
- [ ] Enable HTTPS/SSL for all endpoints
- [ ] Set `DEBUG=false` in production
- [ ] Use environment-specific database URLs
- [ ] Enable firewall rules (only 80/443 open)
- [ ] Configure rate limiting (consider nginx rate limiting)
- [ ] Set up automated backups
- [ ] Configure log rotation

### Post-Deployment

- [ ] Verify health checks are passing
- [ ] Test authentication flow
- [ ] Test case creation and calculation
- [ ] Monitor error logs for first 24 hours
- [ ] Set up monitoring alerts (uptime, error rates)
- [ ] Document incident response procedures

---

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker logs inheritance-backend-prod

# Common issues:
# 1. Database connection - verify DATABASE_URL
# 2. Neo4j connection - verify NEO4J_URI
# 3. Missing environment variables - check .env file
```

### Frontend Build Failures

```bash
# Check Node version
node --version  # Should be 20+

# Clear cache and rebuild
rm -rf .next node_modules
npm install
npm run build
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
docker exec -it inheritance-postgres-prod psql -U inheritance_user -d inheritance_db -c "SELECT 1"

# Test Neo4j connection
docker exec -it inheritance-neo4j-prod cypher-shell -u neo4j -p your-password "RETURN 1"
```

### Migration Conflicts

```bash
# View current revision
uv run alembic current

# View migration history
uv run alembic history

# Resolve conflicts by manually editing migration files
# Then run:
uv run alembic upgrade head
```

---

## Performance Optimization

### Backend

- Use connection pooling for PostgreSQL
- Enable Redis caching (optional)
- Configure Gunicorn with multiple workers
- Set up CDN for static assets

### Frontend

- Enable Next.js Image Optimization
- Configure proper cache headers
- Use CDN for static files
- Enable compression in nginx

### Database

- Add indexes for frequently queried fields
- Configure Neo4j memory settings based on graph size
- Regular VACUUM and ANALYZE for PostgreSQL

---

## Cost Estimation

### VPS (DigitalOcean/Linode)
- Server: $12-20/month (2GB RAM, 2 vCPUs)
- Domain: $10-15/year
- SSL: Free (Let's Encrypt)
- **Total**: ~$15/month

### PaaS (Render/Railway)
- Backend: $7/month
- Frontend: $0 (static hosting)
- PostgreSQL: $7/month
- Neo4j: $7/month (Docker service)
- **Total**: ~$21/month

### Cloud (AWS/GCP)
- EC2/Compute: $20-50/month
- RDS PostgreSQL: $20-40/month
- Neo4j: $30-50/month (self-hosted)
- Load Balancer: $18/month
- **Total**: $88-158/month

---

## Support

For issues and questions:
- GitHub Issues: [Repository URL]
- Documentation: `/docs` endpoint on running backend
- Deployment Checklist: `DEPLOYMENT_CHECKLIST.md`
