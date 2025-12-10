import fitz  # PyMuPDF
import re


class PDFTextExtractor:
    """Extract reference numbers from PDF invoices"""
    
    def extract_reference_from_pdf(self, pdf_path):
        """
        Extract the reference number from the PDF's "Ref" field.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            dict: {'success': bool, 'reference': str, 'error': str}
        """
        try:
            doc = fitz.open(pdf_path)
            page = doc[0]  # First page only
            
            # Extract all text from the page
            text = page.get_text()
            
            # Look for "Ref" field and extract the value
            # The structure is:
            # Ref
            # Customer PO No
            # DENLOU1-15
            #
            # We need to extract the line after "Customer PO No" or the line after "Ref"
            # Pattern: Find "Ref" then skip "Customer PO No" and get the next non-empty line
            
            # Split text into lines
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            reference = None
            for i, line in enumerate(lines):
                if line.lower() == 'ref':
                    # Look at the next few lines
                    # Skip "Customer PO No" if present
                    for j in range(i + 1, min(i + 4, len(lines))):
                        candidate = lines[j]
                        # Skip "Customer PO No" and "Customer:" labels
                        if candidate.lower() in ['customer po no', 'customer:', 'customer']:
                            continue
                        # Check if this looks like a reference (has letters and/or numbers, no spaces)
                        if candidate and ' ' not in candidate and len(candidate) > 1:
                            reference = candidate
                            break
                    if reference:
                        break
            
            doc.close()
            
            if reference:
                # Clean up the reference (remove any trailing punctuation)
                reference = reference.rstrip('.,;:')
                
                print(f"Extracted reference from PDF: {reference}")
                return {
                    'success': True,
                    'reference': reference,
                    'error': None
                }
            else:
                print("Could not find 'Ref' field in PDF")
                return {
                    'success': False,
                    'reference': None,
                    'error': 'Could not find reference field in PDF'
                }
                
        except Exception as e:
            print(f"Error extracting reference from PDF: {e}")
            return {
                'success': False,
                'reference': None,
                'error': str(e)
            }
    
    def extract_reference_from_filename(self, filename):
        """
        Extract reference from filename as fallback.
        
        Expected format: WG_Invoice{NUMBER}_{REFERENCE}_{DATE}_{TIME}.pdf
        Example: WG_Invoice23432_DENLOU1-15_9_Dec_2025_1116_am.pdf
        
        Args:
            filename: Name of the file
            
        Returns:
            dict: {'success': bool, 'reference': str, 'error': str}
        """
        try:
            # Remove .pdf extension
            name = filename.replace('.pdf', '')
            
            # Split by underscore
            parts = name.split('_')
            
            # Reference should be at index 2 (after WG and Invoice{NUM})
            if len(parts) >= 3:
                reference = parts[2]
                
                # Validate it looks like a reference (not a date or time)
                # References should not be purely numeric and should have some letters
                if reference and not reference.isdigit() and re.search(r'[A-Za-z]', reference):
                    print(f"Extracted reference from filename: {reference}")
                    return {
                        'success': True,
                        'reference': reference,
                        'error': None
                    }
            
            print(f"Could not extract reference from filename: {filename}")
            return {
                'success': False,
                'reference': None,
                'error': 'Filename does not match expected format'
            }
            
        except Exception as e:
            print(f"Error extracting reference from filename: {e}")
            return {
                'success': False,
                'reference': None,
                'error': str(e)
            }
    
    def extract_reference(self, pdf_path, filename):
        """
        Extract reference from PDF, with filename fallback.
        
        Args:
            pdf_path: Path to the PDF file
            filename: Name of the file
            
        Returns:
            dict: {'success': bool, 'reference': str, 'source': str, 'error': str}
        """
        # Try PDF extraction first
        result = self.extract_reference_from_pdf(pdf_path)
        
        if result['success']:
            result['source'] = 'pdf'
            return result
        
        # Fallback to filename extraction
        print("PDF extraction failed, trying filename...")
        result = self.extract_reference_from_filename(filename)
        
        if result['success']:
            result['source'] = 'filename'
            return result
        
        # Both methods failed
        result['source'] = None
        return result
