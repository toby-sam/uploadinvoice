# Starting invoice number
STARTING_INVOICE_NUMBER = 380812351

# Directories
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
TEMP_FOLDER = 'temp'

# Invoice tracker file
INVOICE_TRACKER_FILE = 'invoice_tracker.json'

# PDF Coordinates (based on the sample PDF analysis)
# These coordinates are for A4 size (595 x 842 points)
# Coordinates are in points from bottom-left origin

# Invoice number position (top right area)
INVOICE_NUMBER_X = 480
INVOICE_NUMBER_Y = 750

# Invoice date position (below invoice number)
INVOICE_DATE_X = 480
INVOICE_DATE_Y = 730

# Option column area to white out (approximate)
OPTION_COLUMN_X = 50
OPTION_COLUMN_Y = 200
OPTION_COLUMN_WIDTH = 60
OPTION_COLUMN_HEIGHT = 400

# Header area to white out (timestamp and URL)
HEADER_TIMESTAMP_X = 50
HEADER_TIMESTAMP_Y = 800
HEADER_TIMESTAMP_WIDTH = 200
HEADER_TIMESTAMP_HEIGHT = 30

HEADER_URL_X = 300
HEADER_URL_Y = 800
HEADER_URL_WIDTH = 250
HEADER_URL_HEIGHT = 30

# Font settings
FONT_NAME = 'Helvetica'
FONT_SIZE = 10
FONT_SIZE_LARGE = 12

# Server settings
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True
