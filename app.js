// Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// State
let uploadedFile = null;
let processedFilename = null;

// DOM Elements
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const removeFileBtn = document.getElementById('remove-file');
const invoiceNumberInput = document.getElementById('invoice-number');
const invoiceDateInput = document.getElementById('invoice-date');
const customerABNInput = document.getElementById('customer-abn');
const processBtn = document.getElementById('process-btn');
const downloadBtn = document.getElementById('download-btn');
const statusMessage = document.getElementById('status-message');
const statusIcon = document.getElementById('status-icon');
const statusText = document.getElementById('status-text');
const pdfPreview = document.getElementById('pdf-preview');
const previewPlaceholder = document.getElementById('preview-placeholder');
const spinner = document.getElementById('spinner');
const nextInvoiceNumberDisplay = document.getElementById('next-invoice-number');
const processedCountDisplay = document.getElementById('processed-count');
const autoExtractToggle = document.getElementById('auto-extract-toggle');
const excludeDiscountToggle = document.getElementById('exclude-discount-toggle');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeDatePicker();
    fetchNextInvoiceNumber();
    setupEventListeners();
    loadProcessedCount();
});

// Set today's date as default
function initializeDatePicker() {
    const today = new Date().toISOString().split('T')[0];
    invoiceDateInput.value = today;
}

// Fetch next invoice number from server
async function fetchNextInvoiceNumber() {
    try {
        const response = await fetch(`${API_BASE_URL}/next-invoice-number`);
        const data = await response.json();

        if (data.success) {
            invoiceNumberInput.value = data.invoiceNumber;
            nextInvoiceNumberDisplay.textContent = data.invoiceNumber;
        }
    } catch (error) {
        console.error('Error fetching invoice number:', error);
        showStatus('error', 'Failed to fetch invoice number. Using default.');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Dropzone click
    dropzone.addEventListener('click', () => fileInput.click());

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    dropzone.addEventListener('dragover', handleDragOver);
    dropzone.addEventListener('dragleave', handleDragLeave);
    dropzone.addEventListener('drop', handleDrop);

    // Remove file
    removeFileBtn.addEventListener('click', removeFile);

    // Process button
    processBtn.addEventListener('click', processInvoice);

    // Download button
    downloadBtn.addEventListener('click', downloadProcessedPDF);

    // Auto-extract toggle
    autoExtractToggle.addEventListener('change', handleAutoExtractToggle);
}

// Handle auto-extract toggle
function handleAutoExtractToggle() {
    const isEnabled = autoExtractToggle.checked;

    // Disable/enable manual inputs (ABN is always editable)
    invoiceNumberInput.disabled = isEnabled;
    invoiceDateInput.disabled = isEnabled;

    // If enabled and file is uploaded, try to extract
    if (isEnabled && uploadedFile) {
        extractFromFilename(uploadedFile.name);
    } else if (!isEnabled) {
        // Re-fetch next invoice number when switching back to manual
        fetchNextInvoiceNumber();
        initializeDatePicker();
    }
}

// Handle drag over
function handleDragOver(e) {
    e.preventDefault();
    dropzone.classList.add('drag-over');
}

// Handle drag leave
function handleDragLeave(e) {
    e.preventDefault();
    dropzone.classList.remove('drag-over');
}

// Handle drop
function handleDrop(e) {
    e.preventDefault();
    dropzone.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// Handle file select
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// Handle file
function handleFile(file) {
    if (file.type !== 'application/pdf') {
        showStatus('error', 'Please upload a PDF file');
        return;
    }

    uploadedFile = file;

    // Display file info
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.classList.add('active');

    // Enable process button
    processBtn.disabled = false;

    // Show preview
    showPDFPreview(file);

    // If auto-extract is enabled, parse filename
    if (autoExtractToggle.checked) {
        extractFromFilename(file.name);
    }

    showStatus('success', 'File uploaded successfully');
}

// Extract invoice details from filename
async function extractFromFilename(filename) {
    try {
        const response = await fetch(`${API_BASE_URL}/parse-filename`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filename })
        });

        const data = await response.json();

        if (data.success) {
            invoiceNumberInput.value = data.invoice_number;
            invoiceDateInput.value = data.invoice_date;
            showStatus('success', `Extracted: Invoice #${data.invoice_number}, Date: ${data.invoice_date}`);
        } else {
            showStatus('error', `Failed to extract: ${data.error}`);
            // Disable auto-extract on failure
            autoExtractToggle.checked = false;
            handleAutoExtractToggle();
        }
    } catch (error) {
        console.error('Error extracting from filename:', error);
        showStatus('error', 'Failed to parse filename');
        autoExtractToggle.checked = false;
        handleAutoExtractToggle();
    }
}

// Remove file
function removeFile() {
    uploadedFile = null;
    processedFilename = null;
    fileInput.value = '';
    fileInfo.classList.remove('active');
    processBtn.disabled = true;
    downloadBtn.disabled = true;

    // Hide preview
    pdfPreview.classList.remove('active');
    previewPlaceholder.style.display = 'block';

    showStatus('info', 'File removed');
}

// Show PDF preview
async function showPDFPreview(file) {
    try {
        const arrayBuffer = await file.arrayBuffer();
        const blob = new Blob([arrayBuffer], { type: 'application/pdf' });

        // For preview, we'll convert first page to image
        // This is a simplified preview - in production you might use PDF.js
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/preview`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            pdfPreview.src = url;
            pdfPreview.classList.add('active');
            previewPlaceholder.style.display = 'none';
        }
    } catch (error) {
        console.error('Error showing preview:', error);
        // If preview fails, just hide placeholder
        previewPlaceholder.style.display = 'none';
    }
}

// Process invoice
async function processInvoice() {
    if (!uploadedFile) {
        showStatus('error', 'Please upload a PDF file first');
        return;
    }

    const invoiceNumber = invoiceNumberInput.value.trim();
    const invoiceDate = invoiceDateInput.value;
    const customerABN = customerABNInput.value.trim();
    const excludeDiscount = excludeDiscountToggle.checked;

    if (!invoiceNumber || !invoiceDate) {
        showStatus('error', 'Please fill in all required fields');
        return;
    }

    // Show loading
    processBtn.disabled = true;
    spinner.classList.add('active');
    pdfPreview.classList.remove('active');
    previewPlaceholder.style.display = 'none';
    showStatus('info', 'Processing invoice...');

    try {
        const formData = new FormData();
        formData.append('file', uploadedFile);
        formData.append('invoiceNumber', invoiceNumber);
        formData.append('invoiceDate', invoiceDate);
        formData.append('customerABN', customerABN);
        formData.append('excludeDiscount', excludeDiscount);

        const response = await fetch(`${API_BASE_URL}/process-invoice`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            processedFilename = data.filename;

            // Update preview with processed PDF
            const previewResponse = await fetch(`${API_BASE_URL}/preview-processed/${processedFilename}`);
            if (previewResponse.ok) {
                const blob = await previewResponse.blob();
                const url = URL.createObjectURL(blob);
                pdfPreview.src = url;
                pdfPreview.classList.add('active');
            }

            // Enable download
            downloadBtn.disabled = false;

            // Update stats
            incrementProcessedCount();
            await fetchNextInvoiceNumber();

            showStatus('success', 'Invoice processed successfully!');
        } else {
            throw new Error(data.message || 'Processing failed');
        }
    } catch (error) {
        console.error('Error processing invoice:', error);
        showStatus('error', `Processing failed: ${error.message}`);
        pdfPreview.classList.remove('active');
        previewPlaceholder.style.display = 'block';
    } finally {
        spinner.classList.remove('active');
        processBtn.disabled = false;
    }
}

// Download processed PDF
async function downloadProcessedPDF() {
    if (!processedFilename) {
        showStatus('error', 'No processed file available');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/download/${processedFilename}`);

        if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = processedFilename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            showStatus('success', 'Download started!');
        } else {
            throw new Error('Download failed');
        }
    } catch (error) {
        console.error('Error downloading file:', error);
        showStatus('error', 'Download failed');
    }
}

// Show status message
function showStatus(type, message) {
    statusMessage.className = 'status-message active ' + type;

    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };

    statusIcon.textContent = icons[type] || 'ℹ️';
    statusText.textContent = message;

    // Auto-hide after 5 seconds for success/info
    if (type !== 'error') {
        setTimeout(() => {
            statusMessage.classList.remove('active');
        }, 5000);
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Load processed count from localStorage
function loadProcessedCount() {
    const today = new Date().toISOString().split('T')[0];
    const stored = localStorage.getItem('processedInvoices');

    if (stored) {
        const data = JSON.parse(stored);
        if (data.date === today) {
            processedCountDisplay.textContent = data.count;
        } else {
            // Reset for new day
            localStorage.setItem('processedInvoices', JSON.stringify({ date: today, count: 0 }));
            processedCountDisplay.textContent = '0';
        }
    } else {
        localStorage.setItem('processedInvoices', JSON.stringify({ date: today, count: 0 }));
    }
}

// Increment processed count
function incrementProcessedCount() {
    const today = new Date().toISOString().split('T')[0];
    const stored = localStorage.getItem('processedInvoices');

    let count = 0;
    if (stored) {
        const data = JSON.parse(stored);
        if (data.date === today) {
            count = data.count + 1;
        } else {
            count = 1;
        }
    } else {
        count = 1;
    }

    localStorage.setItem('processedInvoices', JSON.stringify({ date: today, count }));
    processedCountDisplay.textContent = count;
}
