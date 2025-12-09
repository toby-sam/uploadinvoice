# Invoice PDF Processor - Linux Server Deployment Guide

This guide will help you deploy the Invoice PDF Processor on your Linux servers.

## Prerequisites

- Linux server (Ubuntu 20.04+, Debian, CentOS, or similar)
- SSH access to the server
- Sudo privileges
- Python 3.8 or higher

---

## Quick Deployment (Ubuntu/Debian)

### Step 1: Prepare the Server

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install nginx (reverse proxy)
sudo apt install nginx -y

# Install supervisor (process manager)
sudo apt install supervisor -y
```

### Step 2: Upload Your Application

```bash
# Create application directory
sudo mkdir -p /var/www/invoice-processor
sudo chown $USER:$USER /var/www/invoice-processor

# Upload files (from your Windows machine)
# Option A: Using SCP
scp -r "c:\WebDevelopment\antigravity\upload invoice\*" user@your-server:/var/www/invoice-processor/

# Option B: Using Git (recommended)
cd /var/www/invoice-processor
git clone YOUR_REPO_URL .
```

### Step 3: Set Up Python Environment

```bash
cd /var/www/invoice-processor

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test the application
python server.py
# Press Ctrl+C to stop
```

### Step 4: Configure Gunicorn

Create `/var/www/invoice-processor/gunicorn_config.py`:

```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
errorlog = "/var/log/invoice-processor/error.log"
accesslog = "/var/log/invoice-processor/access.log"
loglevel = "info"
```

Create log directory:
```bash
sudo mkdir -p /var/log/invoice-processor
sudo chown $USER:$USER /var/log/invoice-processor
```

### Step 5: Configure Supervisor (Auto-Start Service)

Create `/etc/supervisor/conf.d/invoice-processor.conf`:

```ini
[program:invoice-processor]
directory=/var/www/invoice-processor
command=/var/www/invoice-processor/venv/bin/gunicorn -c gunicorn_config.py server:app
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/invoice-processor/err.log
stdout_logfile=/var/log/invoice-processor/out.log
```

Start the service:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start invoice-processor
sudo supervisorctl status invoice-processor
```

### Step 6: Configure Nginx (Reverse Proxy)

Create `/etc/nginx/sites-available/invoice-processor`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Change this to your domain or IP

    client_max_body_size 50M;  # Allow large PDF uploads

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for large file processing
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/invoice-processor /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

### Step 7: Configure Firewall

```bash
# Allow HTTP traffic
sudo ufw allow 80/tcp

# Allow HTTPS (if using SSL)
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

---

## Optional: Enable HTTPS with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

---

## File Permissions Setup

```bash
cd /var/www/invoice-processor

# Set ownership
sudo chown -R www-data:www-data .

# Set directory permissions
sudo find . -type d -exec chmod 755 {} \;

# Set file permissions
sudo find . -type f -exec chmod 644 {} \;

# Make sure invoice_tracker.json is writable
sudo chmod 664 invoice_tracker.json
sudo chown www-data:www-data invoice_tracker.json

# Create uploads directory if it doesn't exist
sudo mkdir -p uploads processed
sudo chown www-data:www-data uploads processed
sudo chmod 755 uploads processed
```

---

## Management Commands

### View Application Logs
```bash
# Supervisor logs
sudo tail -f /var/log/invoice-processor/out.log
sudo tail -f /var/log/invoice-processor/err.log

# Nginx logs
sudo tail -f /var/nginx/access.log
sudo tail -f /var/nginx/error.log
```

### Restart Application
```bash
sudo supervisorctl restart invoice-processor
```

### Stop Application
```bash
sudo supervisorctl stop invoice-processor
```

### Update Application
```bash
cd /var/www/invoice-processor
git pull  # If using git
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart invoice-processor
```

---

## Backup Invoice Tracker

Create a daily backup cron job:

```bash
# Edit crontab
crontab -e

# Add this line (backup daily at 2 AM)
0 2 * * * cp /var/www/invoice-processor/invoice_tracker.json /var/www/invoice-processor/backups/invoice_tracker_$(date +\%Y\%m\%d).json
```

Create backup directory:
```bash
mkdir -p /var/www/invoice-processor/backups
```

---

## Monitoring and Maintenance

### Check Service Status
```bash
sudo supervisorctl status invoice-processor
sudo systemctl status nginx
```

### Monitor Disk Space
```bash
df -h
du -sh /var/www/invoice-processor/uploads
```

### Clean Old Uploads (Optional)
```bash
# Delete uploads older than 30 days
find /var/www/invoice-processor/uploads -type f -mtime +30 -delete
```

---

## Security Best Practices

### 1. Add Basic Authentication (Optional)

Install apache2-utils:
```bash
sudo apt install apache2-utils -y
```

Create password file:
```bash
sudo htpasswd -c /etc/nginx/.htpasswd accounts
```

Update nginx config:
```nginx
location / {
    auth_basic "Invoice Processor";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    proxy_pass http://127.0.0.1:8000;
    # ... rest of config
}
```

Restart nginx:
```bash
sudo systemctl restart nginx
```

### 2. Restrict Access by IP (Optional)

Add to nginx config:
```nginx
location / {
    allow 192.168.1.0/24;  # Your office network
    deny all;
    
    proxy_pass http://127.0.0.1:8000;
    # ... rest of config
}
```

### 3. Enable Fail2Ban
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Troubleshooting

### Application Won't Start
```bash
# Check logs
sudo tail -f /var/log/invoice-processor/err.log

# Check permissions
ls -la /var/www/invoice-processor/invoice_tracker.json

# Test manually
cd /var/www/invoice-processor
source venv/bin/activate
python server.py
```

### Can't Access from Browser
```bash
# Check nginx status
sudo systemctl status nginx

# Check if port is listening
sudo netstat -tlnp | grep :80

# Check firewall
sudo ufw status
```

### File Upload Fails
```bash
# Check nginx client_max_body_size
sudo nano /etc/nginx/sites-available/invoice-processor

# Check upload directory permissions
ls -la /var/www/invoice-processor/uploads
```

---

## Access Your Application

After deployment, your team can access the application at:

- **HTTP**: `http://your-server-ip/` or `http://your-domain.com/`
- **HTTPS**: `https://your-domain.com/` (if SSL configured)

Example: `http://192.168.1.50/` or `https://invoices.yourcompany.com/`

---

## Performance Tuning

For high-traffic scenarios:

### Increase Gunicorn Workers
Edit `gunicorn_config.py`:
```python
workers = (2 * CPU_CORES) + 1  # e.g., 9 for 4-core server
```

### Enable Nginx Caching
Add to nginx config:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g;

location /static/ {
    proxy_cache my_cache;
    proxy_pass http://127.0.0.1:8000;
}
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start app | `sudo supervisorctl start invoice-processor` |
| Stop app | `sudo supervisorctl stop invoice-processor` |
| Restart app | `sudo supervisorctl restart invoice-processor` |
| View logs | `sudo tail -f /var/log/invoice-processor/out.log` |
| Check status | `sudo supervisorctl status` |
| Restart nginx | `sudo systemctl restart nginx` |
| Update code | `cd /var/www/invoice-processor && git pull && sudo supervisorctl restart invoice-processor` |

---

## Next Steps

1. Deploy to your Linux server following the steps above
2. Test the application thoroughly
3. Share the URL with your accounts team
4. Set up regular backups of `invoice_tracker.json`
5. Monitor logs for any issues

Your invoice processor will now be running 24/7 with automatic restarts and professional-grade reliability!
