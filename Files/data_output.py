import json
import csv
import openpyxl
from io import StringIO, BytesIO
def clean_json_string(json_string):
    """
    Removes triple quotes from the beginning and end of a JSON string.

    Args:
        json_string: The JSON string with triple quotes.

    Returns:
        The cleaned JSON string without triple quotes.
    """
    if json_string.startswith("\"\"\"") and json_string.endswith("\"\"\""):
        return json_string[3:-3]
    else:
        return json_string

def json_to_csv(json_data):
    """
    Converts JSON data to CSV format and returns it as a string, preserving special characters.

    Args:
        json_data: The JSON data to be converted.

    Returns:
        A string containing the CSV data.
    """
    json_data = json.loads(json_data)
    output = StringIO()
    fieldnames = ['shop', 'item', 'quantity', 'price', 'currency']
    writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL, quotechar='"')
    writer.writeheader()

    for receipt in json_data.get('receipts', []):
        for item in receipt.get('items', []):
            writer.writerow({
                'shop': receipt.get('shop', ''),
                'item': item.get('item', ''),
                'quantity': item.get('quantity', 1),
                'price': item.get('price', 0),
                'currency': receipt.get('currency', ''),
            })
    
    # Return the CSV data as a string with UTF-8 encoding to preserve special characters
    return output.getvalue().encode('utf-8').decode('utf-8')

def json_to_xls(json_data):
    """
    Converts JSON data to XLSX format and returns it as a BytesIO object, preserving special characters.

    Args:
        json_data: The JSON data to be converted.

    Returns:
        A BytesIO object containing the XLSX data.
    """
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    json_data = json.loads(json_data)
    sheet.append(['shop', 'item', 'quantity', 'price', 'currency'])

    for receipt in json_data.get('receipts', []):
        for item in receipt.get('items', []):
            sheet.append([
                receipt.get('shop', ''),
                item.get('item', ''),
                item.get('quantity', 1),
                item.get('price', 0),
                receipt.get('currency', ''),
            ])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)  # Move the pointer to the beginning of the BytesIO object
    
    # Return the XLSX data as a BytesIO object
    return output

