import sys
import os
import pandas as pd

# Add the project root to sys.path
sys.path.append(os.getcwd())

from utils.export import ReportExporter

def test_pdf_generation():
    metrics = {
        'Ventas': '$1,000,000',
        'Órdenes': '100',
        'Promedio': '$10,000'
    }
    
    print("Generating PDF...")
    try:
        filename = ReportExporter.export_to_pdf(metrics)
        print(f"PDF generated successfully: {filename}")
        if os.path.exists(filename):
            print(f"File size: {os.path.getsize(filename)} bytes")
            # Clean up
            # os.remove(filename)
        else:
            print("Error: File was not created.")
    except Exception as e:
        print(f"Error during PDF generation: {e}")

if __name__ == "__main__":
    test_pdf_generation()
