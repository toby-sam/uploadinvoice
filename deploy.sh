#!/bin/bash
# Quick deployment script for Linux servers

echo "========================================="
echo "Invoice PDF Processor - Quick Deploy"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo"
    exit 1
fi

# Variables
APP_DIR="/var/www/invoice-processor"
APP_USER="www-data"
VENV_DIR="$APP_DIR/venv"

echo "Step 1: Installing system dependencies..."
apt update
apt install -y python3 python3-pip python3-venv nginx supervisor

echo ""
echo "Step 2: Creating application directory..."
mkdir -p $APP_DIR
mkdir -p /var/log/invoice-processor

echo ""
echo "Step 3: Setting up Python virtual environment..."
cd $APP_DIR
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Step 4: Setting file permissions..."
chown -R $APP_USER:$APP_USER $APP_DIR
chown -R $APP_USER:$APP_USER /var/log/invoice-processor
chmod 664 $APP_DIR/invoice_tracker.json
chmod 755 $APP_DIR/uploads
chmod 755 $APP_DIR/processed

echo ""
echo "Step 5: Configuring Supervisor..."
cat > /etc/supervisor/conf.d/invoice-processor.conf << 'EOF'
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
EOF

supervisorctl reread
supervisorctl update
supervisorctl start invoice-processor

echo ""
echo "Step 6: Configuring Nginx..."
cat > /etc/nginx/sites-available/invoice-processor << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
EOF

ln -sf /etc/nginx/sites-available/invoice-processor /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

echo ""
echo "Step 7: Configuring firewall..."
ufw allow 80/tcp
ufw allow 443/tcp

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Application Status:"
supervisorctl status invoice-processor
echo ""
echo "Access your application at:"
echo "http://$(hostname -I | awk '{print $1}')/"
echo ""
echo "Useful commands:"
echo "  View logs: sudo tail -f /var/log/invoice-processor/out.log"
echo "  Restart: sudo supervisorctl restart invoice-processor"
echo "  Status: sudo supervisorctl status invoice-processor"
echo ""
