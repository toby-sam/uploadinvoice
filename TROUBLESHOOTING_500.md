# Server 500 Error - Troubleshooting Guide

## Problem

Getting 500 Internal Server Error when processing invoices on the remote server.

## Most Likely Cause

Missing Python dependencies or system libraries on the server.

---

## Quick Fix (Run on Server)

### Step 1: SSH to Your Server

```bash
ssh user@your-server
cd /var/www/invoice-processor
```

### Step 2: Activate Virtual Environment

```bash
source venv/bin/activate
```

### Step 3: Install/Update Dependencies

```bash
# Install from requirements-linux.txt (recommended for Linux)
pip install -r requirements-linux.txt

# OR install from requirements.txt
pip install -r requirements.txt
```

### Step 4: Verify Critical Packages

```bash
python3 << 'EOF'
try:
    import fitz  # PyMuPDF
    print("✓ PyMuPDF installed:", fitz.__version__)
except ImportError:
    print("✗ PyMuPDF MISSING - this is critical!")

try:
    from PIL import Image
    print("✓ Pillow installed")
except ImportError:
    print("✗ Pillow MISSING")

try:
    import PyPDF2
    print("✓ PyPDF2 installed")
except ImportError:
    print("✗ PyPDF2 MISSING")
EOF
```

### Step 5: Restart the Application

```bash
sudo supervisorctl restart invoice-processor
```

### Step 6: Check Logs for Errors

```bash
# View last 30 lines of error log
sudo tail -30 /var/log/invoice-processor/err.log

# Watch logs in real-time
sudo tail -f /var/log/invoice-processor/out.log
```

---

## Detailed Diagnostic Steps

### 1. Upload Diagnostic Script

From your Windows machine:

```powershell
scp "c:\WebDevelopment\antigravity\upload invoice\diagnose_server.sh" user@your-server:/var/www/invoice-processor/
```

### 2. Run Diagnostic on Server

```bash
ssh user@your-server
cd /var/www/invoice-processor
chmod +x diagnose_server.sh
./diagnose_server.sh
```

This will check:

- ✓ All required files exist
- ✓ Python version
- ✓ Installed packages
- ✓ Directory permissions
- ✓ Service status
- ✓ Recent error logs

---

## Common Issues & Solutions

### Issue 1: PyMuPDF Not Installed

**Symptom**: Error importing `fitz` module

**Solution**:

```bash
cd /var/www/invoice-processor
source venv/bin/activate
pip install PyMuPDF==1.26.6
sudo supervisorctl restart invoice-processor
```

### Issue 2: Permission Denied Errors

**Symptom**: Can't write to uploads/output directories

**Solution**:

```bash
cd /var/www/invoice-processor
sudo chown -R www-data:www-data uploads output temp
sudo chmod 755 uploads output temp
sudo supervisorctl restart invoice-processor
```

### Issue 3: invoice_tracker.json Not Writable

**Symptom**: Can't increment invoice number

**Solution**:

```bash
cd /var/www/invoice-processor
sudo chown www-data:www-data invoice_tracker.json
sudo chmod 664 invoice_tracker.json
sudo supervisorctl restart invoice-processor
```

### Issue 4: Old Code Still Running

**Symptom**: Changes not taking effect

**Solution**:

```bash
cd /var/www/invoice-processor
git pull origin main  # Pull latest code
sudo supervisorctl restart invoice-processor
# Wait 5 seconds, then check status
sudo supervisorctl status invoice-processor
```

### Issue 5: Gunicorn Not Starting

**Symptom**: Service shows as FATAL or STOPPED

**Solution**:

```bash
# Check what's wrong
sudo supervisorctl status invoice-processor

# Try starting manually to see error
cd /var/www/invoice-processor
source venv/bin/activate
gunicorn -c gunicorn_config.py server:app

# If it works, restart via supervisor
sudo supervisorctl restart invoice-processor
```

---

## Testing After Fix

### 1. Check Service Status

```bash
sudo supervisorctl status invoice-processor
# Should show: RUNNING
```

### 2. Check Logs

```bash
# Should show no errors
sudo tail -20 /var/log/invoice-processor/err.log
```

### 3. Test from Browser

1. Open browser on another computer
2. Go to: `http://your-server-ip/`
3. Upload a PDF invoice
4. Click "Process Invoice"
5. Should work without 500 error

---

## Full Reinstall (If All Else Fails)

```bash
# Stop the service
sudo supervisorctl stop invoice-processor

# Remove old virtual environment
cd /var/www/invoice-processor
rm -rf venv

# Create fresh virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements-linux.txt

# Set permissions
sudo chown -R www-data:www-data /var/www/invoice-processor
sudo chmod 755 uploads output temp
sudo chmod 664 invoice_tracker.json

# Restart service
sudo supervisorctl restart invoice-processor

# Check status
sudo supervisorctl status invoice-processor
```

---

## Getting Help

If you're still seeing errors, collect this information:

```bash
# 1. Service status
sudo supervisorctl status invoice-processor

# 2. Last 50 lines of error log
sudo tail -50 /var/log/invoice-processor/err.log > ~/error_log.txt

# 3. Installed packages
source /var/www/invoice-processor/venv/bin/activate
pip list > ~/packages.txt

# 4. Python version
python3 --version > ~/python_version.txt
```

Then review the error_log.txt to see the actual Python error.

---

## Prevention

To avoid this in the future:

1. **Always test on server after deploying**
2. **Keep requirements.txt updated** when adding new dependencies
3. **Monitor logs regularly**: `sudo tail -f /var/log/invoice-processor/err.log`
4. **Set up alerts** for service failures

---

## Quick Command Reference

| Task            | Command                                                                         |
| --------------- | ------------------------------------------------------------------------------- |
| View error logs | `sudo tail -f /var/log/invoice-processor/err.log`                               |
| Restart service | `sudo supervisorctl restart invoice-processor`                                  |
| Check status    | `sudo supervisorctl status invoice-processor`                                   |
| Test manually   | `cd /var/www/invoice-processor && source venv/bin/activate && python server.py` |
| Install deps    | `pip install -r requirements-linux.txt`                                         |
| Fix permissions | `sudo chown -R www-data:www-data /var/www/invoice-processor`                    |
