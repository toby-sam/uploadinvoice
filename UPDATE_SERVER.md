# Quick Server Update Guide

This guide will help you update your Linux server with the latest changes (favicon fix).

## Files Changed

The following files have been updated:

- ✅ `favicon.svg` - **NEW FILE** (favicon icon)
- ✅ `index.html` - Added favicon link tag
- ✅ `server.py` - Added favicon route handler

---

## Option 1: Manual Update (Recommended for Quick Fix)

### Step 1: Upload the New/Modified Files

From your Windows machine, upload the files to the server:

```bash
# Upload favicon.svg (NEW FILE)
scp "c:\WebDevelopment\antigravity\upload invoice\favicon.svg" user@your-server:/var/www/invoice-processor/

# Upload updated index.html
scp "c:\WebDevelopment\antigravity\upload invoice\index.html" user@your-server:/var/www/invoice-processor/

# Upload updated server.py
scp "c:\WebDevelopment\antigravity\upload invoice\server.py" user@your-server:/var/www/invoice-processor/
```

**Replace `user@your-server` with your actual SSH credentials.**

### Step 2: Set File Permissions

SSH into your server and run:

```bash
ssh user@your-server

# Navigate to app directory
cd /var/www/invoice-processor

# Set correct ownership
sudo chown www-data:www-data favicon.svg index.html server.py

# Set correct permissions
sudo chmod 644 favicon.svg index.html server.py
```

### Step 3: Restart the Application

```bash
# Restart the application
sudo supervisorctl restart invoice-processor

# Check status
sudo supervisorctl status invoice-processor

# View logs to confirm no errors
sudo tail -f /var/log/invoice-processor/out.log
```

Press `Ctrl+C` to stop viewing logs.

---

## Option 2: Using Git (If You Have a Repository)

### Step 1: Commit and Push Changes

From your Windows machine:

```bash
cd "c:\WebDevelopment\antigravity\upload invoice"

# Add the new and modified files
git add favicon.svg index.html server.py

# Commit the changes
git commit -m "Add favicon to fix 500 error for remote users"

# Push to your repository
git push origin main
```

### Step 2: Pull Changes on Server

SSH into your server:

```bash
ssh user@your-server

# Navigate to app directory
cd /var/www/invoice-processor

# Pull latest changes
git pull origin main

# Restart the application
sudo supervisorctl restart invoice-processor

# Check status
sudo supervisorctl status invoice-processor
```

---

## Option 3: Using the Deploy Script

If you want to do a full redeployment:

### Step 1: Upload All Files

```bash
# From Windows, upload everything
scp -r "c:\WebDevelopment\antigravity\upload invoice\*" user@your-server:/var/www/invoice-processor/
```

### Step 2: Run Deploy Script

```bash
ssh user@your-server

cd /var/www/invoice-processor

# Make deploy script executable
chmod +x deploy.sh

# Run deployment (requires sudo)
sudo ./deploy.sh
```

---

## Verify the Update

After updating, test from a different computer:

1. Open a browser on another computer
2. Navigate to: `http://your-server-ip/`
3. Check the browser console (F12) - there should be **NO** favicon errors
4. The favicon should appear in the browser tab

---

## What This Update Fixes

✅ **Fixes the 500 Internal Server Error** for `/favicon.ico` requests  
✅ **Adds a professional favicon** to the browser tab  
✅ **Improves user experience** for remote users accessing the server

The favicon is a blue document icon that represents the invoice processing application.

---

## Troubleshooting

### If the favicon still doesn't show:

1. **Clear browser cache** on the client computer (Ctrl+Shift+Delete)
2. **Hard refresh** the page (Ctrl+F5)
3. **Check file permissions**:
   ```bash
   ls -la /var/www/invoice-processor/favicon.svg
   # Should show: -rw-r--r-- www-data www-data
   ```

### If you see errors in the logs:

```bash
# View error logs
sudo tail -f /var/log/invoice-processor/err.log

# View application logs
sudo tail -f /var/log/invoice-processor/out.log

# View nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### If the application won't restart:

```bash
# Stop the application
sudo supervisorctl stop invoice-processor

# Check for syntax errors
cd /var/www/invoice-processor
source venv/bin/activate
python server.py
# Press Ctrl+C if it starts successfully

# Start via supervisor
sudo supervisorctl start invoice-processor
```

---

## Quick Command Reference

| Task          | Command                                                                         |
| ------------- | ------------------------------------------------------------------------------- |
| Upload file   | `scp "local\file" user@server:/var/www/invoice-processor/`                      |
| Restart app   | `sudo supervisorctl restart invoice-processor`                                  |
| View logs     | `sudo tail -f /var/log/invoice-processor/out.log`                               |
| Check status  | `sudo supervisorctl status invoice-processor`                                   |
| Test manually | `cd /var/www/invoice-processor && source venv/bin/activate && python server.py` |

---

## Summary

The update adds a favicon to prevent browser errors when users access the application from different computers. The changes are minimal and low-risk:

- **1 new file**: `favicon.svg`
- **2 modified files**: `index.html` (1 line added), `server.py` (5 lines added)

Total deployment time: **~2 minutes**
