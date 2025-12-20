# Deployment Guide

## Local Development

### Requirements
- Python 3.11+
- pip
- Virtual environment

### Setup

```bash
# Clone/navigate to project
cd contract-intelligence-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python utils.py setup-db

# Run development server
python utils.py dev
```

The API will be available at `http://localhost:8000`

## Docker Deployment

### Quick Start

```bash
# Copy environment file
cp .env.example .env

# Start services
docker-compose up -d

# Check status
docker-compose ps
curl http://localhost:8000/admin/healthz
```

### Docker Commands

```bash
# View logs
docker-compose logs -f contract-api

# Stop services
docker-compose down

# Rebuild image
docker-compose build --no-cache

# Run one-off command
docker-compose exec contract-api python -c "..."
```

## Production Deployment

### 1. Database Setup

Switch from SQLite to PostgreSQL:

```bash
# Create database
createdb contract_db
createuser contract_user -P

# Set environment variable
DATABASE_URL=postgresql://contract_user:password@localhost:5432/contract_db
```

### 2. Environment Configuration

Create `.env` for production:

```env
DEBUG=false
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4-turbo-preview
DATABASE_URL=postgresql://...
MAX_FILE_SIZE=100
```

### 3. Kubernetes Deployment

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: contract-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: contract-api
  template:
    metadata:
      labels:
        app: contract-api
    spec:
      containers:
      - name: contract-api
        image: contract-intelligence-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /admin/healthz
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: contract-api-service
spec:
  selector:
    app: contract-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy:

```bash
kubectl apply -f k8s-deployment.yaml
```

### 4. Using AWS ECS

Create task definition `task-definition.json`:

```json
{
  "family": "contract-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "contract-api",
      "image": "YOUR_ECR_URI:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://..."
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/contract-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register and run:

```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
aws ecs create-service --cluster default --service-name contract-api \
  --task-definition contract-api --desired-count 2 \
  --launch-type FARGATE --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}"
```

### 5. Using Heroku

Create `Procfile`:

```
web: python main.py
```

Deploy:

```bash
heroku login
heroku create contract-intelligence-api
git push heroku main
```

### 6. Using DigitalOcean App Platform

Create `app.yaml`:

```yaml
name: contract-api
services:
- name: api
  build:
    dockerfile_path: Dockerfile
  http_port: 8000
  env:
  - key: DATABASE_URL
    scope: RUN_AND_BUILD_TIME
    value: ${db.username}:${db.password}@${db.host}:${db.port}/${db.name}
  health_check:
    http_path: /admin/healthz
  http_routes:
  - path: /
databases:
- engine: PG
  name: db
  version: "14"
```

## Monitoring & Logging

### Application Metrics

The API exposes Prometheus-compatible metrics (can be added):

```python
from prometheus_client import Counter, Histogram

ingest_counter = Counter('contract_ingests_total', 'Total ingests')
extraction_duration = Histogram('extraction_duration_seconds', 'Extraction time')
```

### Log Aggregation

Using ELK Stack:

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - ./logs/*.log

output.elasticsearch:
  hosts: ["localhost:9200"]
```

### Health Monitoring

Setup monitoring alerts:

```bash
# Check health every 30 seconds
watch -n 30 'curl -s http://localhost:8000/admin/healthz | jq'

# Alert if down
curl -f http://localhost:8000/admin/healthz || send_alert
```

## Performance Tuning

### 1. Database Optimization

```sql
CREATE INDEX idx_contract_id ON query_logs(contract_id);
CREATE INDEX idx_created_at ON contracts(upload_date);
```

### 2. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_document(doc_id: str):
    # Cached results
    pass
```

### 3. Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40
)
```

### 4. Async Processing

Use task queue for long-running operations:

```python
from celery import Celery

celery = Celery()

@celery.task
async def extract_fields_async(doc_id):
    # Long-running extraction
    pass
```

## Backup & Recovery

### Database Backup

```bash
# PostgreSQL
pg_dump contract_db > backup_$(date +%Y%m%d).sql

# Restore
psql contract_db < backup_20250115.sql
```

### File Backup

```bash
# Backup uploaded PDFs
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/uploads/

# Restore
tar -xzf data_backup_20250115.tar.gz
```

## Security Hardening

### 1. API Authentication

Add JWT authentication:

```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/ingest")
async def ingest(credentials: HTTPAuthenticationCredentials = Depends(security)):
    token = credentials.credentials
    # Validate JWT
```

### 2. HTTPS

```bash
# Use Let's Encrypt with Nginx
certbot certonly --standalone -d api.example.com
```

### 3. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/ingest")
@limiter.limit("100/minute")
async def ingest():
    pass
```

### 4. Input Validation

Already handled by Pydantic, but add extra validation:

```python
from pydantic import validator

class AskRequest(BaseModel):
    question: str
    
    @validator('question')
    def question_not_empty(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Question too short')
        return v
```

## Troubleshooting

### High Memory Usage

Check for memory leaks:

```bash
pip install memory-profiler
python -m memory_profiler main.py
```

### Slow Queries

Enable query logging:

```python
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### PDF Extraction Issues

Use different PDF library:

```python
# Try pypdf instead of pdfplumber
import pypdf
reader = pypdf.PdfReader("file.pdf")
```

## Maintenance

### Regular Tasks

- Monitor disk usage: `df -h`
- Check database size: `du -sh data/db/`
- Review logs for errors: `tail -f logs/app.log`
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Backup data regularly

### Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild Docker image
docker-compose build --no-cache

# Restart services
docker-compose restart
```
