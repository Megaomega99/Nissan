# Deployment Guide

This guide covers different deployment options for the EV Battery Predictor application.

## Prerequisites

- Docker and Docker Compose installed
- Git for cloning the repository
- Domain name (for production deployment)
- SSL certificates (for HTTPS)

## Development Deployment

### Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd ev-battery-predictor
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Start all services:
```bash
docker-compose up --build
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### First Time Setup

1. Create a user account through the frontend registration
2. Add a vehicle in the Vehicles section
3. Upload battery data (CSV/Excel format)
4. Create and train ML models
5. Generate predictions

## Production Deployment

### Environment Setup

1. Set production environment variables:
```bash
export POSTGRES_PASSWORD=your_secure_database_password
export SECRET_KEY=your_very_long_and_secure_secret_key
export BACKEND_URL=https://your-domain.com
```

2. Configure SSL certificates (place in `./ssl/` directory):
```
ssl/
├── cert.pem
└── key.pem
```

3. Update nginx configuration if needed (`nginx.conf`)

### Deploy with Docker Compose

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### Health Checks

Monitor service health:
```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
```

## Cloud Deployment Options

### AWS ECS/Fargate

1. Build and push images to ECR:
```bash
# Backend
docker build -t ev-predictor-backend ./backend
docker tag ev-predictor-backend:latest <aws-account>.dkr.ecr.<region>.amazonaws.com/ev-predictor-backend:latest
docker push <aws-account>.dkr.ecr.<region>.amazonaws.com/ev-predictor-backend:latest

# Frontend
docker build -f ./frontend/Dockerfile.prod -t ev-predictor-frontend ./frontend
docker tag ev-predictor-frontend:latest <aws-account>.dkr.ecr.<region>.amazonaws.com/ev-predictor-frontend:latest
docker push <aws-account>.dkr.ecr.<region>.amazonaws.com/ev-predictor-frontend:latest
```

2. Create ECS task definitions and services
3. Set up Application Load Balancer
4. Configure RDS for PostgreSQL
5. Use ElastiCache for Redis

### Google Cloud Run

1. Build and deploy backend:
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/ev-predictor-backend ./backend
gcloud run deploy ev-predictor-backend --image gcr.io/PROJECT-ID/ev-predictor-backend --platform managed
```

2. Build and deploy frontend:
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/ev-predictor-frontend ./frontend
gcloud run deploy ev-predictor-frontend --image gcr.io/PROJECT-ID/ev-predictor-frontend --platform managed
```

3. Set up Cloud SQL for PostgreSQL
4. Use Memorystore for Redis

### Azure Container Instances

1. Create resource group and container registry
2. Build and push images to ACR
3. Deploy using container groups
4. Set up Azure Database for PostgreSQL
5. Use Azure Cache for Redis

## Database Management

### Backup

```bash
# Create backup
docker exec -t <postgres-container> pg_dump -U evuser evbattery > backup.sql

# Restore backup
docker exec -i <postgres-container> psql -U evuser -d evbattery < backup.sql
```

### Migrations

Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

Create new migration:
```bash
docker-compose exec backend alembic revision --autogenerate -m "migration description"
```

## Monitoring and Logging

### Application Logs

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# With timestamps
docker-compose logs -f -t backend
```

### Database Monitoring

```bash
# Connect to database
docker-compose exec db psql -U evuser -d evbattery

# Check connections
SELECT * FROM pg_stat_activity;

# Check database size
SELECT pg_size_pretty(pg_database_size('evbattery'));
```

### Performance Monitoring

Monitor key metrics:
- API response times
- Database query performance
- Model training completion rates
- File upload success rates
- User authentication metrics

## Security Considerations

### Production Security

1. **Environment Variables**: Never commit secrets to version control
2. **Database**: Use strong passwords and network isolation
3. **SSL/TLS**: Always use HTTPS in production
4. **JWT Secrets**: Use cryptographically secure random keys
5. **File Uploads**: Validate file types and sizes
6. **CORS**: Configure appropriate origins
7. **Rate Limiting**: Implement API rate limiting
8. **Updates**: Keep dependencies updated

### Recommended Security Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

## Scaling

### Horizontal Scaling

1. **Backend**: Scale FastAPI workers
```yaml
backend:
  deploy:
    replicas: 3
```

2. **Database**: Use read replicas for heavy read workloads
3. **Redis**: Use Redis Cluster for high availability
4. **Load Balancer**: Distribute traffic across instances

### Vertical Scaling

Increase resource limits:
```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
```

## Troubleshooting

### Common Issues

1. **Database Connection**: Check DATABASE_URL and network connectivity
2. **File Uploads**: Verify MAX_FILE_SIZE and disk space
3. **Model Training**: Check available memory and CPU resources
4. **CORS Errors**: Verify BACKEND_CORS_ORIGINS configuration
5. **JWT Errors**: Ensure SECRET_KEY is consistent across restarts

### Debug Mode

Enable debug logging:
```yaml
backend:
  environment:
    - LOG_LEVEL=DEBUG
```

### Health Check Endpoints

- Backend: `GET /health`
- Database: Check via backend health endpoint
- Redis: Check via backend health endpoint

## Maintenance

### Regular Tasks

1. **Database Backups**: Schedule regular backups
2. **Log Rotation**: Configure log rotation
3. **Security Updates**: Keep base images updated
4. **Model Cleanup**: Archive old models
5. **Data Retention**: Implement data retention policies

### Update Deployment

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Check health
docker-compose -f docker-compose.prod.yml ps
```