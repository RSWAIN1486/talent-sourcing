# Deployment Guide

## Prerequisites

### System Requirements
- Python 3.11 or higher
- Node.js 18 or higher
- MongoDB 6.0 or higher
- Git

### Required Accounts
- MongoDB Atlas account
- DeepInfra API account

## Local Development Setup

### Backend Setup

1. **Create and activate conda environment**
```bash
conda create -n talent_sourcing python=3.11
conda activate talent_sourcing
```

2. **Install backend dependencies**
```bash
cd backend
pip install -e .
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run database migrations**
```bash
alembic upgrade head
```

5. **Start backend server**
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. **Install frontend dependencies**
```bash
cd frontend
npm install
```

2. **Start development server**
```bash
npm run dev
```

## Production Deployment

### Backend Deployment

1. **Server Requirements**
   - Ubuntu 20.04 LTS or higher
   - Python 3.11
   - Nginx
   - Supervisor

2. **Installation Steps**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv nginx supervisor

# Create application directory
sudo mkdir /opt/talent-sourcing
sudo chown $USER:$USER /opt/talent-sourcing

# Clone repository
git clone <repository-url> /opt/talent-sourcing

# Create virtual environment
python3.11 -m venv /opt/talent-sourcing/venv
source /opt/talent-sourcing/venv/bin/activate

# Install dependencies
cd /opt/talent-sourcing/backend
pip install -e .
```

3. **Configure Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. **Configure Supervisor**
```ini
[program:talent-sourcing]
command=/opt/talent-sourcing/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/opt/talent-sourcing/backend
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/talent-sourcing.err.log
stdout_logfile=/var/log/talent-sourcing.out.log
```

### Frontend Deployment

1. **Build frontend**
```bash
cd frontend
npm run build
```

2. **Configure Nginx for frontend**
```nginx
server {
    listen 80;
    server_name app.your-domain.com;
    root /opt/talent-sourcing/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## Environment Variables

### Backend (.env)
```env
# MongoDB settings
MONGODB_USERNAME=your-username
MONGODB_PASSWORD=your-password
MONGODB_CLUSTER=your-cluster
MONGODB_URL=mongodb+srv://${MONGODB_USERNAME}:${MONGODB_PASSWORD}@${MONGODB_CLUSTER}
MONGODB_DB_NAME=talent_sourcing

# JWT settings
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI API settings
AI_API_KEY=your-deepinfra-api-key
AI_BASE_URL=https://api.deepinfra.com/v1/openai
```

## Monitoring Setup

1. **Install monitoring tools**
```bash
pip install prometheus_client
pip install grafana
```

2. **Configure logging**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/talent-sourcing/app.log'),
        logging.StreamHandler()
    ]
)
```

## Backup Strategy

1. **Database Backup**
```bash
# Create backup script
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mongodump --uri="mongodb+srv://..." --out="/backup/mongodb_$TIMESTAMP"

# Compress backup
tar -czf "/backup/mongodb_$TIMESTAMP.tar.gz" "/backup/mongodb_$TIMESTAMP"

# Remove uncompressed backup
rm -rf "/backup/mongodb_$TIMESTAMP"
```

2. **File Storage Backup**
```bash
# Backup GridFS files
mongodump --uri="mongodb+srv://..." --collection=fs.files --collection=fs.chunks
```

## Security Checklist

1. **SSL/TLS Configuration**
   - Install SSL certificate
   - Configure HTTPS
   - Enable HSTS

2. **Firewall Setup**
   - Configure UFW
   - Allow only necessary ports
   - Set up rate limiting

3. **Security Headers**
   - Set X-Frame-Options
   - Set Content-Security-Policy
   - Enable XSS protection

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check MongoDB connection string
   - Verify network connectivity
   - Check IP whitelist

2. **File Upload Issues**
   - Check upload directory permissions
   - Verify GridFS connection
   - Check file size limits

3. **Performance Issues**
   - Monitor server resources
   - Check database indexes
   - Review application logs 