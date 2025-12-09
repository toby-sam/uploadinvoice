import fitz  # PyMuPDF
from datetime import datetime
import os

class SimplePDFProcessor:
    """Simplified PDF processor that only adds invoice number and date overlay"""
    
    def process_invoice(self, input_pdf_path, invoice_number, invoice_date, output_pdf_path, customer_abn='', exclude_discount=True):
        """
        Add invoice number, date, and customer ABN to the header table fields
        
        Args:
            input_pdf_path: Path to input PDF
            invoice_number: Invoice number to add
            invoice_date: Invoice date to add (YYYY-MM-DD format)
            output_pdf_path: Path to save processed PDF
            customer_abn: Customer ABN (optional)
            exclude_discount: Whether to hide discount line on page 2 (default: True)
        """
        try:
            # Open the PDF
            doc = fitz.open(input_pdf_path)
            
            # Format the date
            formatted_date = self._format_date(invoice_date)
            
            # Process all pages to remove header and footer
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Remove header (timestamp and URL) from top of page
                # Reduced height to preserve William Green logo - only remove top 15 pixels
                header_rect = fitz.Rect(0, 0, page.rect.width, 15)
                page.draw_rect(header_rect, color=(1, 1, 1), fill=(1, 1, 1))
                
                # Remove footer (URL) from bottom of page
                # Footer is at the very bottom, approximately last 30 pixels
                footer_rect = fitz.Rect(0, page.rect.height - 30, page.rect.width, page.rect.height)
                page.draw_rect(footer_rect, color=(1, 1, 1), fill=(1, 1, 1))
                
                # On page 2 (index 1), hide Amount Paid line if requested
                if page_num == 1 and exclude_discount:
                    # Cover the Total Paid (AUD) line with white rectangle
                    # Final position: X: 403-568, Y: 325-335
                    discount_rect = fitz.Rect(403, 325, 568, 335)
                    page.draw_rect(discount_rect, color=(1, 1, 1), fill=(1, 1, 1))
            
            # Now process first page for invoice details
            page = doc[0]
            
            # Get page dimensions
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            print(f"Page dimensions: {page_width} x {page_height}")
            
            # Position for header table fields (based on PDF text analysis)
            # ADJUSTABLE POSITIONS - modify these values to fine-tune placement
            
            # Invoice Number position
            invoice_num_x = 300  # X position for invoice number
            invoice_num_y = 104  # Y position for invoice number (moved up from 114)
            
            # Invoice Date position  
            invoice_date_x = 372  # X position for invoice date
            invoice_date_y = 104  # Y position for invoice date (moved up from 114)
            
            # Customer ABN position (to the right of invoice date)
            customer_abn_x = 445  # X position for ABN
            customer_abn_y = 104  # Y position (same as invoice date)
            
            # Header label positions (above the numbers)
            header_offset_y = 10  # How far above the numbers to place headers
            
            # Cover "Customer PO No" label with white rectangle
            black_rect = fitz.Rect(250, 70, 380, 95)
            page.draw_rect(black_rect, color=(1, 1, 1), fill=(1, 1, 1))
            
            print(f"Invoice Number position: x={invoice_num_x}, y={invoice_num_y}")
            print(f"Invoice Date position: x={invoice_date_x}, y={invoice_date_y}")
            
            # Add "Invoice No" header
            page.insert_text(
                (invoice_num_x, invoice_num_y - header_offset_y),
                "Invoice No",
                fontsize=9,
                fontname="Helvetica-Bold",
                color=(0, 0, 0)
            )
            
            # Add invoice number below the header
            page.insert_text(
                (invoice_num_x, invoice_num_y),
                invoice_number,
                fontsize=9,
                fontname="Helvetica",
                color=(0, 0, 0)
            )
            
            # Add "Invoice Date" header
            page.insert_text(
                (invoice_date_x, invoice_date_y - header_offset_y),
                "Invoice Date",
                fontsize=9,
                fontname="Helvetica-Bold",
                color=(0, 0, 0)
            )
            
            # Add invoice date below the header
            page.insert_text(
                (invoice_date_x, invoice_date_y),
                formatted_date,
                fontsize=9,
                fontname="Helvetica",
                color=(0, 0, 0)
            )
            
            # Add Customer ABN if provided
            if customer_abn:
                page.insert_text(
                    (customer_abn_x, customer_abn_y - header_offset_y),
                    "Customer ABN",
                    fontsize=9,
                    fontname="Helvetica-Bold",
                    color=(0, 0, 0)
                )
                page.insert_text(
                    (customer_abn_x, customer_abn_y),
                    customer_abn,
                    fontsize=9,
                    fontname="Helvetica",
                    color=(0, 0, 0)
                )
            
            # Save the modified PDF
            page_count = len(doc)
            doc.save(output_pdf_path)
            doc.close()
            
            print(f"Successfully added invoice #{invoice_number} at Ref and date {formatted_date} at Customer PO No")
            print(f"Removed header from all {page_count} pages")
            return True
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _format_date(self, date_string):
        """Format date string to DD/MM/YYYY"""
        try:
            # Input format: YYYY-MM-DD
            date_obj = datetime.strptime(date_string, '%Y-%m-%d')
            # Output format: DD/MM/YYYY
            return date_obj.strftime('%d/%m/%Y')
        except:
            return date_string
    
    def generate_preview(self, pdf_path, output_image_path):
        """
        Generate a preview image of the PDF
        
        Args:
            pdf_path: Path to PDF file
            output_image_path: Path to save preview image
        """
        try:
            doc = fitz.open(pdf_path)
            page = doc[0]
            
            # Render at 2x for preview
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            pix.save(output_image_path)
            
            doc.close()
            return True
        except Exception as e:
            print(f"Error generating preview: {e}")
            return False
