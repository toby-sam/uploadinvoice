from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import config
from pdf_processor import SimplePDFProcessor

app = Flask(__name__)
CORS(app)

# Create necessary directories
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)
os.makedirs(config.TEMP_FOLDER, exist_ok=True)

# Initialize PDF processor
pdf_processor = SimplePDFProcessor()

def get_invoice_tracker():
    """Load invoice tracker from JSON file"""
    if os.path.exists(config.INVOICE_TRACKER_FILE):
        with open(config.INVOICE_TRACKER_FILE, 'r') as f:
            return json.load(f)
    else:
        # Initialize with starting number
        return {
            'last_invoice_number': config.STARTING_INVOICE_NUMBER - 1,
            'last_updated': datetime.now().isoformat()
        }

def save_invoice_tracker(tracker):
    """Save invoice tracker to JSON file"""
    tracker['last_updated'] = datetime.now().isoformat()
    with open(config.INVOICE_TRACKER_FILE, 'w') as f:
        json.dump(tracker, f, indent=2)

def get_next_invoice_number():
    """Get the next invoice number"""
    tracker = get_invoice_tracker()
    next_number = tracker['last_invoice_number'] + 1
    return next_number

def increment_invoice_number():
    """Increment and save the invoice number"""
    tracker = get_invoice_tracker()
    tracker['last_invoice_number'] += 1
    save_invoice_tracker(tracker)
    return tracker['last_invoice_number']

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_file(path)

@app.route('/api/next-invoice-number', methods=['GET'])
def api_next_invoice_number():
    """Get the next invoice number"""
    try:
        next_number = get_next_invoice_number()
        return jsonify({
            'success': True,
            'invoiceNumber': str(next_number)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/parse-filename', methods=['POST'])
def api_parse_filename():
    """Parse invoice number and date from filename"""
    try:
        from filename_parser import parse_invoice_from_filename
        
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({
                'success': False,
                'error': 'No filename provided'
            }), 400
        
        result = parse_invoice_from_filename(filename)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/preview', methods=['POST'])
def api_preview():
    """Generate preview of uploaded PDF"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'success': False, 'message': 'File must be a PDF'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_pdf_path = os.path.join(config.TEMP_FOLDER, f'preview_{filename}')
        file.save(temp_pdf_path)
        
        # Generate preview image
        preview_image_path = os.path.join(config.TEMP_FOLDER, f'preview_{filename}.png')
        success = pdf_processor.generate_preview(temp_pdf_path, preview_image_path)
        
        if success:
            return send_file(preview_image_path, mimetype='image/png')
        else:
            return jsonify({'success': False, 'message': 'Failed to generate preview'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/process-invoice', methods=['POST'])
def api_process_invoice():
    """Process the uploaded invoice PDF"""
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['file']
        invoice_number = request.form.get('invoiceNumber')
        invoice_date = request.form.get('invoiceDate')
        customer_abn = request.form.get('customerABN', '')  # Optional field
        exclude_discount = request.form.get('excludeDiscount', 'true') == 'true'  # Default to true
        
        if not invoice_number or not invoice_date:
            return jsonify({'success': False, 'message': 'Missing invoice details'}), 400
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'success': False, 'message': 'File must be a PDF'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        input_filename = f'{timestamp}_{filename}'
        input_path = os.path.join(config.UPLOAD_FOLDER, input_filename)
        file.save(input_path)
        
        # Generate output filename
        output_filename = f'invoice_{invoice_number}_{timestamp}.pdf'
        output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)
        
        # Process the PDF
        success = pdf_processor.process_invoice(
            input_path,
            invoice_number,
            invoice_date,
            output_path,
            customer_abn,
            exclude_discount
        )
        
        if success:
            # Increment invoice number for next use
            increment_invoice_number()
            
            return jsonify({
                'success': True,
                'message': 'Invoice processed successfully',
                'filename': output_filename
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to process invoice'
            }), 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/preview-processed/<filename>', methods=['GET'])
def api_preview_processed(filename):
    """Generate preview of processed PDF"""
    try:
        pdf_path = os.path.join(config.OUTPUT_FOLDER, filename)
        
        if not os.path.exists(pdf_path):
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        # Generate preview
        preview_path = os.path.join(config.TEMP_FOLDER, f'processed_{filename}.png')
        success = pdf_processor.generate_preview(pdf_path, preview_path)
        
        if success:
            return send_file(preview_path, mimetype='image/png')
        else:
            return jsonify({'success': False, 'message': 'Failed to generate preview'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def api_download(filename):
    """Download processed PDF"""
    try:
        return send_from_directory(
            config.OUTPUT_FOLDER,
            filename,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'File not found: {str(e)}'
        }), 404

if __name__ == '__main__':
    print(f"Starting Invoice PDF Processor Server...")
    print(f"Server running at http://localhost:{config.PORT}")
    print(f"Starting invoice number: {config.STARTING_INVOICE_NUMBER}")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
