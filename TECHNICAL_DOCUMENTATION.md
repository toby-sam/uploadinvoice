# Invoice PDF Processor - Technical Documentation

## Project Overview

The Invoice PDF Processor is a web-based application that automates the processing of PDF invoices by adding invoice numbers, dates, customer ABN, and modifying specific labels and fields. The application provides a user-friendly interface for uploading PDFs and automatically generates processed versions with the required modifications.

---

## Technology Stack

**Backend:**
- Python 3.x
- Flask (Web Framework)
- PyMuPDF (fitz) - PDF manipulation
- Gunicorn - Production WSGI server

**Frontend:**
- HTML5
- CSS3 (Vanilla CSS with modern design)
- JavaScript (ES6+)

**Deployment:**
- Nginx (Reverse Proxy)
- Supervisor (Process Management)
- Linux (Ubuntu/Debian)

---

## Project Structure

```
upload invoice/
├── Core Application Files
│   ├── server.py              # Flask server & API endpoints
│   ├── pdf_processor.py       # PDF manipulation logic
│   ├── filename_parser.py     # Filename parsing utilities
│   ├── config.py              # Application configuration
│   ├── index.html             # Web interface
│   ├── app.js                 # Frontend JavaScript
│   └── style.css              # Application styling
│
├── Deployment Files
│   ├── requirements.txt       # Python dependencies
│   ├── gunicorn_config.py     # Gunicorn configuration
│   ├── Procfile               # Process file for deployment
│   ├── deploy.sh              # Deployment script
│   ├── DEPLOYMENT.md          # General deployment guide
│   ├── LINUX_DEPLOYMENT.md    # Linux server deployment guide
│   └── README.md              # Project documentation
│
├── Data
│   └── invoice_tracker.json   # Invoice number counter (CRITICAL)
│
└── Runtime Directories
    ├── uploads/               # Temporary uploaded files
    ├── output/                # Processed PDF files
    └── temp/                  # Temporary processing files
```

---

## Core Features

### 1. Invoice Number & Date Stamping
- Automatically adds invoice number and date to PDF header
- Positions: Invoice Number (X=300, Y=104), Invoice Date (X=372, Y=104)
- Maintains sequential invoice numbering via `invoice_tracker.json`

### 2. Customer ABN Field
- Optional field for Australian Business Number
- Position: X=445, Y=104
- Always editable (independent of auto-extract feature)
- Displayed on PDF next to Invoice Date

### 3. Auto-Extract from Filename
- Parses invoice number and date from filename
- Expected format: `WG_Invoice{NUMBER}_{REF}_{DAY}_{MONTH}_{YEAR}_{TIME}.pdf`
- Example: `WG_Invoice23432_DENLOU1-15_9_Dec_2025_1116_am.pdf`
- Automatically populates form fields when enabled

### 4. Total Paid Exclusion
- Toggle to hide "Total Paid (AUD)" line on page 2
- Uses white rectangle overlay at X: 403-568, Y: 325-335
- Enabled by default

### 5. Label Modifications
- **Customer → Invoice To:** Changes "Customer:" label to "Invoice To:"
  - Position: X: 14-80, Y: 113-128
- **Customer PO No:** Covered with white rectangle
  - Position: X: 250-380, Y: 70-95

### 6. Header/Footer Removal
- Removes header from all pages (top 15 pixels)
- Removes footer from all pages (bottom 30 pixels)
- Preserves William Green logo

---

## File Descriptions

### server.py
**Purpose:** Flask web server and API endpoints

**Key Functions:**
- `index()` - Serves the web interface
- `api_next_invoice_number()` - Returns next invoice number
- `api_parse_filename()` - Parses filename for invoice data
- `api_preview()` - Generates PDF preview image
- `api_process_invoice()` - Main processing endpoint
- `api_preview_processed()` - Preview processed PDF
- `api_download()` - Download processed PDF

**API Endpoints:**
- `GET /` - Web interface
- `GET /api/next-invoice-number` - Get next invoice number
- `POST /api/parse-filename` - Parse filename
- `POST /api/preview` - Generate preview
- `POST /api/process-invoice` - Process invoice
- `GET /api/preview-processed/<filename>` - Preview processed
- `GET /api/download/<filename>` - Download processed

### pdf_processor.py
**Purpose:** PDF manipulation and processing

**Class:** `SimplePDFProcessor`

**Key Method:** `process_invoice(input_pdf_path, invoice_number, invoice_date, output_pdf_path, customer_abn='', exclude_discount=True)`

**Processing Steps:**
1. Opens PDF with PyMuPDF
2. Removes headers/footers from all pages
3. Applies Total Paid exclusion on page 2 (if enabled)
4. Covers "Customer PO No" label with white rectangle
5. Changes "Customer:" to "Invoice To:" label
6. Adds invoice number, date, and ABN to page 1
7. Saves processed PDF

**Coordinate System:**
- Origin: Top-left corner (0, 0)
- X-axis: Left to right
- Y-axis: Top to bottom
- Standard page size: 595 x 842 points (A4)

### filename_parser.py
**Purpose:** Extract invoice data from filenames

**Key Function:** `parse_invoice_from_filename(filename)`

**Returns:**
```python
{
    'success': bool,
    'invoice_number': str,
    'invoice_date': str,  # YYYY-MM-DD format
    'error': str  # If success is False
}
```

### config.py
**Purpose:** Application configuration

**Key Settings:**
- `STARTING_INVOICE_NUMBER` - Initial invoice number
- `UPLOAD_FOLDER` - Upload directory path
- `OUTPUT_FOLDER` - Output directory path
- `TEMP_FOLDER` - Temporary files directory
- `INVOICE_TRACKER_FILE` - Invoice counter file
- `HOST`, `PORT`, `DEBUG` - Server settings

### index.html
**Purpose:** Web interface structure

**Key Sections:**
- Header with next invoice number display
- File upload dropzone
- Auto-extract toggle
- Invoice details form (number, date, ABN)
- Exclude Total Paid toggle
- Process button
- PDF preview area
- Download button

### app.js
**Purpose:** Frontend logic and API communication

**Key Functions:**
- `fetchNextInvoiceNumber()` - Get next invoice number
- `handleFile()` - Handle file upload
- `extractFromFilename()` - Parse filename
- `handleAutoExtractToggle()` - Toggle auto-extract
- `processInvoice()` - Send to server for processing
- `loadPreview()` - Display PDF preview

### style.css
**Purpose:** Application styling

**Design Features:**
- Modern, clean interface
- Responsive layout
- Dark mode compatible
- Smooth animations
- Custom toggle switches
- Professional color scheme

---

## Application Workflow

### 1. User Uploads PDF
```
User selects PDF → File uploaded to /uploads/ → Preview generated → Displayed in UI
```

### 2. Auto-Extract (Optional)
```
Toggle enabled → Filename parsed → Invoice number & date auto-filled
```

### 3. User Fills Form
```
Invoice Number (auto or manual)
Invoice Date (auto or manual)
Customer ABN (always manual, optional)
Exclude Total Paid (checkbox, default: checked)
```

### 4. Processing
```
User clicks "Process Invoice" →
Server receives request →
PDF Processor:
  1. Removes headers/footers
  2. Applies Total Paid exclusion (if enabled)
  3. Covers "Customer PO No" label
  4. Changes "Customer:" to "Invoice To:"
  5. Adds invoice number, date, ABN
  6. Saves to /output/
→ Preview generated →
Download button enabled
```

### 5. Download
```
User clicks download → Processed PDF downloaded → Invoice number incremented
```

---

## PDF Processing Details

### Coordinate Positions

**Page 1 - Header Fields:**
```python
Invoice Number:  X=300, Y=104
Invoice Date:    X=372, Y=104
Customer ABN:    X=445, Y=104
Header offset:   Y-10 (for labels above values)
```

**Page 1 - Label Modifications:**
```python
Customer PO No cover:    Rect(250, 70, 380, 95)   # White
Customer → Invoice To:   Rect(14, 113, 80, 128)   # White
Invoice To text:         (14, 126)                # Black, Bold, 10pt
```

**Page 2 - Total Paid Exclusion:**
```python
Total Paid cover:        Rect(403, 325, 568, 335) # White
```

**All Pages - Header/Footer:**
```python
Header removal:          Rect(0, 0, width, 15)           # White
Footer removal:          Rect(0, height-30, width, height) # White
```

### Font Specifications
- **Headers:** Helvetica-Bold, 9pt
- **Values:** Helvetica, 9pt
- **Invoice To:** Helvetica-Bold, 10pt

---

## Data Persistence

### invoice_tracker.json
**Purpose:** Maintains sequential invoice numbering

**Structure:**
```json
{
  "current_invoice_number": 380812351,
  "last_updated": "2025-12-09T10:30:00"
}
```

**Critical:** This file must be backed up before deployment and preserved during updates.

---

## Deployment

### Development
```bash
python server.py
# Runs on http://localhost:5000
```

### Production (Linux)
See `LINUX_DEPLOYMENT.md` for complete guide:
1. Install dependencies
2. Configure Gunicorn
3. Set up Supervisor for auto-start
4. Configure Nginx reverse proxy
5. Optional: SSL with Let's Encrypt

---

## Security Considerations

1. **File Upload Validation:** Only PDF files accepted
2. **File Size Limits:** Configured in Flask
3. **Temporary File Cleanup:** Automatic cleanup of temp files
4. **Path Traversal Protection:** Secure file handling
5. **Production Server:** Gunicorn instead of Flask dev server
6. **Firewall:** Configure UFW for port access
7. **HTTPS:** Recommended for production (Let's Encrypt)

---

## Maintenance

### Backup Critical Files
```bash
# Invoice tracker (CRITICAL)
invoice_tracker.json

# Configuration
config.py

# Application files
server.py, pdf_processor.py, filename_parser.py
```

### Monitoring
- Check Supervisor status: `sudo supervisorctl status invoice-processor`
- View logs: `sudo tail -f /var/log/supervisor/invoice-processor.log`
- Nginx logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`

### Updates
1. Backup `invoice_tracker.json`
2. Pull latest code
3. Restart service: `sudo supervisorctl restart invoice-processor`
4. Reload Nginx: `sudo systemctl reload nginx`

---

## Troubleshooting

**Server won't start:**
- Check Python dependencies: `pip install -r requirements.txt`
- Verify port 5000 is available
- Check file permissions

**PDF processing fails:**
- Verify PyMuPDF installation: `pip install PyMuPDF`
- Check input PDF is valid
- Review server logs

**Invoice number not incrementing:**
- Check `invoice_tracker.json` exists and is writable
- Verify file permissions

**Preview not displaying:**
- Check temp directory exists and is writable
- Verify image generation in `pdf_processor.py`

---

## Future Enhancements

Potential improvements:
- Database for invoice tracking
- Multi-user support with authentication
- Batch processing
- Email notifications
- Invoice templates
- Export to accounting software
- Audit logging

---

## Support & Documentation

- **Deployment Guide:** `LINUX_DEPLOYMENT.md`
- **General Deployment:** `DEPLOYMENT.md`
- **Project README:** `README.md`
- **Code Comments:** Inline documentation in all files

---

## Version Information

**Current Version:** 1.0.0
**Last Updated:** December 2025
**Python Version:** 3.8+
**Dependencies:** See `requirements.txt`

---

## License & Credits

**Framework:** Flask (BSD License)
**PDF Library:** PyMuPDF (GNU AGPL)
**Developed:** 2025
