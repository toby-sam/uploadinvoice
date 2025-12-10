#!/bin/bash
# Server Diagnostic Script
# Run this on your Linux server to diagnose issues

echo "========================================="
echo "Invoice Processor - Server Diagnostics"
echo "========================================="
echo ""

APP_DIR="/var/www/invoice-processor"

echo "1. Checking application directory..."
if [ -d "$APP_DIR" ]; then
    echo "✓ Application directory exists: $APP_DIR"
    cd "$APP_DIR"
else
    echo "✗ Application directory NOT found: $APP_DIR"
    exit 1
fi

echo ""
echo "2. Checking required files..."
for file in server.py config.py pdf_processor.py filename_parser.py favicon.svg index.html; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file MISSING"
    fi
done

echo ""
echo "3. Checking Python virtual environment..."
if [ -d "venv" ]; then
    echo "✓ Virtual environment exists"
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "✗ Virtual environment NOT found"
fi

echo ""
echo "4. Checking Python version..."
python3 --version

echo ""
echo "5. Checking installed packages..."
pip list | grep -E "(Flask|PyPDF2|Pillow|pdf2image|gunicorn)"

echo ""
echo "6. Checking required directories..."
for dir in uploads output temp; do
    if [ -d "$dir" ]; then
        echo "✓ $dir/ exists"
        ls -ld "$dir"
    else
        echo "✗ $dir/ MISSING - creating..."
        mkdir -p "$dir"
        chown www-data:www-data "$dir"
        chmod 755 "$dir"
    fi
done

echo ""
echo "7. Checking file permissions..."
ls -la invoice_tracker.json 2>/dev/null || echo "✗ invoice_tracker.json not found"

echo ""
echo "8. Checking supervisor status..."
sudo supervisorctl status invoice-processor

echo ""
echo "9. Checking recent error logs (last 20 lines)..."
echo "--- Error Log ---"
sudo tail -20 /var/log/invoice-processor/err.log 2>/dev/null || echo "No error log found"

echo ""
echo "--- Output Log ---"
sudo tail -20 /var/log/invoice-processor/out.log 2>/dev/null || echo "No output log found"

echo ""
echo "10. Checking system dependencies..."
echo "Checking poppler-utils (required for PDF processing):"
which pdftoppm || echo "✗ pdftoppm NOT installed - run: sudo apt install poppler-utils"

echo ""
echo "11. Testing Python imports..."
python3 << 'PYEOF'
import sys
print("Python executable:", sys.executable)
print("\nTesting imports:")
try:
    import flask
    print("✓ Flask:", flask.__version__)
except ImportError as e:
    print("✗ Flask:", e)

try:
    import PyPDF2
    print("✓ PyPDF2:", PyPDF2.__version__)
except ImportError as e:
    print("✗ PyPDF2:", e)

try:
    from PIL import Image
    print("✓ Pillow (PIL):", Image.__version__)
except ImportError as e:
    print("✗ Pillow:", e)

try:
    import pdf2image
    print("✓ pdf2image: installed")
except ImportError as e:
    print("✗ pdf2image:", e)

try:
    import gunicorn
    print("✓ gunicorn:", gunicorn.__version__)
except ImportError as e:
    print("✗ gunicorn:", e)
PYEOF

echo ""
echo "12. Checking network/ports..."
echo "Checking if port 8000 is listening:"
sudo netstat -tlnp | grep :8000 || echo "✗ Port 8000 not listening"

echo ""
echo "========================================="
echo "Diagnostic Complete!"
echo "========================================="
echo ""
echo "Common fixes:"
echo "1. Missing packages: pip install -r requirements.txt"
echo "2. Missing poppler: sudo apt install poppler-utils"
echo "3. Permission issues: sudo chown -R www-data:www-data $APP_DIR"
echo "4. Restart service: sudo supervisorctl restart invoice-processor"
