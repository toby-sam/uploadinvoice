# Invoice PDF Processing System

## Quick Start

```bash
cd "c:\WebDevelopment\antigravity\upload invoice"
python server.py
```

Then open http://localhost:5000 in your browser.

## What It Does

- Adds invoice numbers to the "Ref" field
- Adds invoice dates to the "Customer PO No" field
- Auto-increments invoice numbers starting from 380812351
- Both fields appear on the same line in the header

## Current Status

✅ Invoice number positioned at Ref field (x=165.8, y=106.6)
✅ Invoice date positioned at Customer PO No field (x=428.2, y=106.6)
✅ Server running at http://localhost:5000
✅ Auto-increment working from 380812351

## Test Output

```
Successfully added invoice #380812351 at Ref and date 09/12/2025 at Customer PO No
Output file size: 227128 bytes
```

The positioning is now correct - both values appear on the same horizontal line in the header table.
