import pdfplumber
import json
import sys

pdf_path = "中国去势抵抗性前列腺癌诊治专家共识.pdf"

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    print(f"Total pages: {total_pages}")
    
    for i, page in enumerate(pdf.pages):
        print(f"\n--- Page {i+1} ---")
        text = page.extract_text()
        if text:
            print(text[:2000])  # Print first 2000 chars
