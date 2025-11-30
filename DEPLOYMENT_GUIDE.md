# Deployment & Implementation Guide

## Quick Start

### 1. Environment Setup

```bash
# Clone environment template
cp .env.example .env

# Edit .env with your values
nano .env

# Key variables to update:
SECRET_KEY=<generate-random-50-char-string>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost:5432/kindergarten
ENVIRONMENT=production
```

### 2. Database Setup

```bash
# Install PostgreSQL locally or via Docker
docker-compose up -d postgres redis

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Create initial tenant
python manage.py shell
>>> from core.models import Tenant
>>> Tenant.objects.create(name="My Kindergarten", slug="my-kindergarten")
```

### 3. Local Testing

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run unit tests
pytest -v --cov

# Run integration tests
pytest integration_tests.py -v

# Run server
python manage.py runserver

# Access API at http://localhost:8000/api/
```

---

## Production Deployment

### Using Docker

```bash
# 1. Build image
docker build -t kindergarten-api:latest .

# 2. Start services
docker-compose up -d

# 3. Run migrations
docker-compose exec web python manage.py migrate

# 4. Create superuser
docker-compose exec web python manage.py createsuperuser

# 5. Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# 6. Check health
curl http://localhost:8000/api/health/
```

### Manual Deployment

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
export SECRET_KEY="your-secret-key"
export DEBUG="False"
export DATABASE_URL="postgresql://..."

# 3. Run migrations
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Start Gunicorn
gunicorn kinderGartenAPI.wsgi:application --bind 0.0.0.0:8000 --workers 4

# 6. Start Celery
celery -A kinderGartenAPI worker -l info

# 7. Start Celery Beat
celery -A kinderGartenAPI beat -l info
```

---

## Monitoring & Maintenance

### Health Check Endpoints

```bash
# API health
curl http://localhost:8000/api/health/

# Database connectivity
curl http://localhost:8000/api/health/db/

# Celery status
curl http://localhost:8000/api/celery-status/
```

### Log Monitoring

```bash
# View application logs
docker-compose logs -f web

# View database logs
docker-compose logs -f postgres

# View Redis logs
docker-compose logs -f redis
```

### Performance Monitoring

```bash
# Access Django Silk
http://localhost:8000/silk/

# Run load tests
locust -f load_tests.py --host http://localhost:8000 -u 100 -r 10 --run-time 5m
```

---

## Troubleshooting

### Migration Errors

```bash
# Check migration status
python manage.py showmigrations

# Roll back specific migration
python manage.py migrate <app> <migration_number>

# Check for conflicts
python manage.py migrate --check
```

### Database Issues

```bash
# Check database connection
python manage.py dbshell

# Verify indexes
python manage.py shell
>>> from django.db import connection
>>> with connection.cursor() as cursor:
>>>     cursor.execute("SELECT indexname FROM pg_indexes")
>>>     for row in cursor.fetchall():
>>>         print(row[0])

# Analyze slow queries
python manage.py querycount
```

### Celery Issues

```bash
# Check active tasks
celery -A kinderGartenAPI inspect active

# Clear task queue
celery -A kinderGartenAPI purge

# View scheduled tasks
celery -A kinderGartenAPI inspect scheduled
```

---

## Backup Strategy

### PostgreSQL Backups

```bash
# Daily backup
pg_dump kindergarten > /backups/kindergarten_$(date +%Y%m%d).sql

# Restore from backup
psql kindergarten < /backups/kindergarten_20240115.sql

# Automated backup script
0 2 * * * pg_dump kindergarten | gzip > /backups/kindergarten_$(date +\%Y\%m\%d).sql.gz
```

### Media Files Backup

```bash
# Backup uploaded files
tar -czf /backups/media_$(date +%Y%m%d).tar.gz /path/to/media/

# Restore
tar -xzf /backups/media_20240115.tar.gz -C /path/to/
```

---

## Performance Optimization

### Database Tuning

```sql
-- Create indexes
CREATE INDEX idx_child_tenant_classroom ON children_child(tenant_id, classroom_id);
CREATE INDEX idx_attendance_tenant_date ON attendance_attendancerecord(tenant_id, date);

-- Analyze queries
EXPLAIN ANALYZE SELECT * FROM children_child WHERE tenant_id = 1;
```

### Redis Caching

```python
# Configure in settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Query Optimization

```python
# Use select_related for ForeignKey
queryset = Child.objects.select_related('classroom', 'parent_user')

# Use prefetch_related for M2M and reverse FK
queryset = Child.objects.prefetch_related('clubs')

# Use only() to limit fields
queryset = Child.objects.only('id', 'name', 'classroom_id')
```

---

## Security Hardening

### HTTPS Configuration

```nginx
# nginx SSL config
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/ssl/certs/your_cert.crt;
    ssl_certificate_key /etc/ssl/private/your_key.key;

    # Redirect HTTP to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}
```

### Rate Limiting

```python
# Configure in settings.py
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/hour',
    'user': '1000/hour',
}
```

### API Key Management

```python
# Use environment variables
API_KEY = os.environ.get('API_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')

# Rotate keys regularly
# Use Django-environ for security
```

---

## CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Tests & Deploy

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements-dev.txt

      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
        run: pytest -v --cov

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: |
          # Your deployment script
          ./scripts/deploy.sh
```

---

## Scaling Considerations

### Horizontal Scaling

```yaml
# docker-compose with multiple workers
services:
  web1:
    build: .
    environment:
      - WORKER_INSTANCE=1
    ports:
      - '8001:8000'

  web2:
    build: .
    environment:
      - WORKER_INSTANCE=2
    ports:
      - '8002:8000'

  nginx:
    image: nginx:latest
    ports:
      - '80:80'
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web1
      - web2
```

### Database Scaling

```python
# Use read replicas for scaling reads
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'kindergarten',
        'HOST': 'primary.rds.amazonaws.com',
    },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'kindergarten',
        'HOST': 'replica.rds.amazonaws.com',
    }
}

# Route reads to replica
class ReadReplicaRouter:
    def db_for_read(self, model, **hints):
        return 'replica'

    def db_for_write(self, model, **hints):
        return 'default'
```

---

## Support & Documentation

### API Documentation

- Swagger UI: `/api/swagger/`
- ReDoc: `/api/redoc/`

### Admin Panel

- URL: `/admin/`
- Default superuser created via `python manage.py createsuperuser`

### Logs & Monitoring

- Application logs: `docker-compose logs -f web`
- Database logs: `docker-compose logs -f postgres`
- Performance monitoring: `/silk/`

### Contact & Support

- Documentation: See `AUDIT_REPORT.md`
- Issues: Report via GitHub Issues
- Email: support@yourdomain.com

---

**Version:** 1.0
**Last Updated:** 2024
**Next Review:** Q2 2024
