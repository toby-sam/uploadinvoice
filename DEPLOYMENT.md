# Invoice PDF Processor - Deployment Guide

This guide will help you deploy the Invoice PDF Processor application so your accounts team can access it.

## Prerequisites

- Python 3.8 or higher
- All dependencies from `requirements.txt` installed
- The application files in a directory

## Deployment Options

### Option 1: Local Network Server (Easiest)

Deploy on a computer within your office network that stays on during business hours.

#### Steps:

1. **Install Python and Dependencies**
   ```bash
   cd "c:\WebDevelopment\antigravity\upload invoice"
   pip install -r requirements.txt
   ```

2. **Configure Server for Network Access**
   
   Edit `server.py` and change the host:
   ```python
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000, debug=False)
   ```

3. **Find Your Computer's IP Address**
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

4. **Start the Server**
   ```bash
   python server.py
   ```

5. **Access from Other Computers**
   
   Team members can access at: `http://YOUR_IP:5000`
   
   Example: `http://192.168.1.100:5000`

#### Pros:
- ✅ Quick setup
- ✅ No cloud costs
- ✅ Data stays on-premises

#### Cons:
- ❌ Server computer must stay on
- ❌ Only accessible within office network
- ❌ Not suitable for remote work

---

### Option 2: Cloud Deployment (Recommended for Remote Teams)

Deploy to a cloud platform for 24/7 availability and remote access.

#### Option 2A: Deploy to Render (Free Tier Available)

1. **Create a Render Account**
   - Go to https://render.com
   - Sign up for free

2. **Prepare Your Code**
   
   Create `render.yaml`:
   ```yaml
   services:
     - type: web
       name: invoice-processor
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: gunicorn server:app
       envVars:
         - key: PYTHON_VERSION
           value: 3.11.0
   ```

3. **Add Gunicorn to requirements.txt**
   ```
   Flask==3.0.0
   flask-cors==4.0.0
   PyMuPDF==1.23.8
   Pillow==10.1.0
   Werkzeug==3.0.1
   gunicorn==21.2.0
   ```

4. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

5. **Deploy on Render**
   - Connect your GitHub repository
   - Render will automatically deploy
   - You'll get a URL like: `https://invoice-processor.onrender.com`

#### Option 2B: Deploy to Railway

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create `Procfile`**
   ```
   web: gunicorn server:app
   ```

3. **Deploy**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Railway will auto-deploy

---

### Option 3: Windows Server / Always-On PC

For organizations with a Windows Server or dedicated PC.

#### Steps:

1. **Install Python**
   - Download from python.org
   - Install for all users

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create Windows Service (Optional)**
   
   Install NSSM (Non-Sucking Service Manager):
   ```bash
   # Download NSSM from nssm.cc
   nssm install InvoiceProcessor "C:\Python311\python.exe" "C:\WebDevelopment\antigravity\upload invoice\server.py"
   nssm start InvoiceProcessor
   ```

4. **Configure Firewall**
   - Open Windows Firewall
   - Allow inbound connections on port 5000

---

## Security Considerations

### For Production Use:

1. **Add Authentication**
   
   Consider adding basic authentication to `server.py`:
   ```python
   from flask_httpauth import HTTPBasicAuth
   
   auth = HTTPBasicAuth()
   
   users = {
       "accounts": "your_password_here"
   }
   
   @auth.verify_password
   def verify_password(username, password):
       if username in users and users[username] == password:
           return username
   
   @app.route('/process', methods=['POST'])
   @auth.login_required
   def process_invoice():
       # existing code
   ```

2. **Use HTTPS**
   - For cloud deployments, HTTPS is usually automatic
   - For local servers, consider using a reverse proxy (nginx)

3. **Backup Invoice Tracker**
   - Regularly backup `invoice_tracker.json`
   - Consider using a database instead of JSON file

4. **Set Environment Variables**
   ```python
   import os
   
   UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
   STARTING_INVOICE = int(os.getenv('STARTING_INVOICE', '380812351'))
   ```

---

## Recommended Setup for Your Team

Based on typical small business needs:

### For Office-Only Access:
**Use Option 1** - Local Network Server
- Simple, free, keeps data on-premises
- Good for teams working from the same office

### For Remote/Hybrid Teams:
**Use Option 2A** - Render Deployment
- Free tier available
- Automatic HTTPS
- Easy to set up
- 24/7 availability

---

## Quick Start Commands

### Local Development:
```bash
cd "c:\WebDevelopment\antigravity\upload invoice"
python server.py
```
Access at: http://localhost:5000

### Network Access:
```bash
# Edit server.py to use host='0.0.0.0'
python server.py
```
Access at: http://YOUR_IP:5000

---

## Troubleshooting

### Port Already in Use:
```bash
# Change port in server.py
app.run(host='0.0.0.0', port=8080)
```

### Can't Access from Other Computers:
- Check firewall settings
- Verify IP address is correct
- Ensure server computer is on same network

### Invoice Number Not Incrementing:
- Check `invoice_tracker.json` permissions
- Ensure file is not read-only

---

## Support

For issues or questions, refer to the README.md file or contact your IT administrator.
