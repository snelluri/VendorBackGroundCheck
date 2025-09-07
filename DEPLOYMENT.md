# Deployment Guide

This guide provides detailed instructions for deploying the Vendor Background Check application in different environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
   - [Docker](#docker)
   - [Manual Setup](#manual-setup)
   - [Cloud Platforms](#cloud-platforms)
4. [Scaling](#scaling)
5. [Monitoring](#monitoring)
6. [Backup and Recovery](#backup-and-recovery)
7. [Security](#security)

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git
- Database (PostgreSQL recommended)
- Web server (Nginx/Apache)
- Application server (Gunicorn/Uvicorn)
- Redis (for caching and rate limiting)

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/vendor-background-check.git
cd vendor-background-check
```

### 2. Set up a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Run the development server

```bash
python -m src.main
```

The application will be available at `http://localhost:8000`

## Production Deployment

### Docker (Recommended)

1. **Install Docker and Docker Compose**

2. **Build and run**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

3. **View logs**
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

### Manual Setup

1. **Install system dependencies**
   ```bash
   # On Ubuntu/Debian
   sudo apt update
   sudo apt install -y python3-pip python3-venv nginx redis-server
   ```

2. **Set up the application**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/vendor-background-check.git
   cd vendor-background-check
   
   # Create and activate virtual environment
   python3 -m venv /opt/venv
   source /opt/venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt gunicorn
   ```

3. **Configure Gunicorn**
   Create `/etc/systemd/system/vendor-check.service`:
   ```ini
   [Unit]
   Description=Vendor Background Check
   After=network.target
   
   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/application
   Environment="PATH=/opt/venv/bin"
   ExecStart=/opt/venv/bin/gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 src.main:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Set up Nginx**
   Create `/etc/nginx/sites-available/vendor-check`:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       location /static/ {
           alias /path/to/application/static/;
           expires 30d;
       }
   }
   ```
   Enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/vendor-check /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. **Start the application**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start vendor-check
   sudo systemctl enable vendor-check
   ```

### Cloud Platforms

#### AWS Elastic Beanstalk

1. Install EB CLI:
   ```bash
   pip install awsebcli
   ```

2. Initialize EB:
   ```bash
   eb init -p python-3.8 vendor-check
   ```

3. Create environment:
   ```bash
   eb create vendor-check-env
   ```

#### Google Cloud Run

1. Create `Dockerfile` and `cloudbuild.yaml`
2. Deploy:
   ```bash
   gcloud run deploy vendor-check --source .
   ```

## Scaling

### Horizontal Scaling

1. **Load Balancing**
   - Use a load balancer (AWS ALB, Nginx, HAProxy)
   - Configure health checks
   
2. **Database**
   - Set up read replicas
   - Implement connection pooling

3. **Caching**
   - Use Redis for distributed caching
   - Implement cache invalidation

### Vertical Scaling

- Increase instance size
- Optimize database queries
- Enable compression
- Use CDN for static assets

## Monitoring

### Logging

- **Application Logs**: Configure in `logging.conf`
- **System Logs**: Use journalctl
- **Centralized Logging**: ELK Stack or CloudWatch

### Metrics

- **Application Metrics**: Prometheus + Grafana
- **System Metrics**: CloudWatch, Datadog
- **Error Tracking**: Sentry

### Alerts

- Set up alerts for:
  - High error rates
  - Response time degradation
  - Resource utilization

## Backup and Recovery

### Database Backups

```bash
# PostgreSQL
pg_dump -U username -d dbname > backup.sql

# Schedule with cron
0 2 * * * pg_dump -U username -d dbname > /backups/db-$(date +\%Y\%m\%d).sql
```

### Application Backups

```bash
# Backup application code and media
rsync -avz /path/to/application user@backup-server:/backups/
```

### Recovery

1. Restore database:
   ```bash
   psql -U username -d dbname < backup.sql
   ```

2. Restore application:
   ```bash
   rsync -avz user@backup-server:/backups/application/ /path/to/application
   ```

## Security

### SSL/TLS

```bash
# Using Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Security Headers

Add to Nginx config:
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

### Regular Updates

- Keep all dependencies updated
- Set up Dependabot for automated dependency updates
- Regularly update the operating system

### Security Scans

```bash
# Dependency scanning
pip-audit

# Static code analysis
bandit -r src/

# Container scanning
trivy image your-image:tag
```

## Maintenance

### Database Migrations

```bash
# Generate migrations
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```

### Scheduled Tasks

Use systemd timers or Celery Beat for scheduled tasks like:
- Database cleanup
- Cache invalidation
- Report generation

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify credentials in `.env`
   - Check if database is running
   - Check connection limits

2. **Rate Limiting**
   - Check Redis connection
   - Adjust rate limits in `.env`

3. **Performance Issues**
   - Check database queries
   - Monitor resource usage
   - Review caching strategy

### Getting Help

- Check logs: `journalctl -u vendor-check -f`
- Enable debug mode in `.env`
- Open an issue on GitHub

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
