"""
Utility functions for parsing invoice information from filenames
"""
import re
from datetime import datetime

def parse_invoice_from_filename(filename):
    """
    Parse invoice number and date from filename
    
    Expected format: WG_Invoice{NUMBER}_{REF}_{DAY}_{MONTH}_{YEAR}_{TIME}.pdf
    Example: WG_Invoice23432_DENLOU1-15_9_Dec_2025_1116_am.pdf
    
    Returns:
        dict: {'invoice_number': str, 'invoice_date': str (YYYY-MM-DD), 'success': bool, 'error': str}
    """
    try:
        # Remove .pdf extension
        name = filename.replace('.pdf', '')
        
        # Pattern: WG_Invoice{NUMBER}_{REF}_{DAY}_{MONTH}_{YEAR}_{TIME}
        # Extract invoice number after "Invoice"
        invoice_match = re.search(r'Invoice(\d+)', name)
        if not invoice_match:
            return {
                'success': False,
                'error': 'Could not find invoice number in filename'
            }
        
        invoice_number = invoice_match.group(1)
        
        # Extract date parts: {DAY}_{MONTH}_{YEAR}
        # Split by underscore and find date components
        parts = name.split('_')
        
        # Find day, month, year pattern
        date_pattern = None
        for i in range(len(parts) - 2):
            # Check if we have day_month_year pattern
            if parts[i].isdigit() and len(parts[i]) <= 2:  # Day
                day = parts[i]
                month = parts[i + 1]
                year = parts[i + 2]
                
                # Validate year is 4 digits
                if year.isdigit() and len(year) == 4:
                    date_pattern = (day, month, year)
                    break
        
        if not date_pattern:
            return {
                'success': False,
                'error': 'Could not find date pattern in filename'
            }
        
        day, month, year = date_pattern
        
        # Convert month name to number
        month_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
        
        month_lower = month.lower()
        month_num = month_map.get(month_lower)
        
        if not month_num:
            return {
                'success': False,
                'error': f'Invalid month: {month}'
            }
        
        # Create date object and format as YYYY-MM-DD
        try:
            date_obj = datetime(int(year), month_num, int(day))
            invoice_date = date_obj.strftime('%Y-%m-%d')
        except ValueError as e:
            return {
                'success': False,
                'error': f'Invalid date: {str(e)}'
            }
        
        return {
            'success': True,
            'invoice_number': invoice_number,
            'invoice_date': invoice_date
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error parsing filename: {str(e)}'
        }


def test_parser():
    """Test the parser with example filename"""
    test_filename = "WG_Invoice23432_DENLOU1-15_9_Dec_2025_1116_am.pdf"
    result = parse_invoice_from_filename(test_filename)
    print(f"Test filename: {test_filename}")
    print(f"Result: {result}")
    
    if result['success']:
        print(f"Invoice Number: {result['invoice_number']}")
        print(f"Invoice Date: {result['invoice_date']}")
    else:
        print(f"Error: {result['error']}")


if __name__ == '__main__':
    test_parser()
