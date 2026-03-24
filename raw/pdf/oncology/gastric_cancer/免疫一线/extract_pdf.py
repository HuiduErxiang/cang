#!/usr/bin/env python3
import json
import sys

try:
    import pdfplumber
    print("Using pdfplumber")
    pdf = pdfplumber.open('KEYNOTE-859补充资料.pdf')
    total_pages = len(pdf.pages)
    print(f"Total pages: {total_pages}")
    
    # Extract text from all pages
    all_text = []
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        all_text.append(f"--- Page {i+1} ---\n{text}")
    
    with open('pdf_content.txt', 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(all_text))
    print("Content saved to pdf_content.txt")
    
except ImportError:
    print("pdfplumber not available, trying PyPDF2...")
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader('KEYNOTE-859补充资料.pdf')
        total_pages = len(reader.pages)
        print(f"Total pages: {total_pages}")
        
        all_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            all_text.append(f"--- Page {i+1} ---\n{text}")
        
        with open('pdf_content.txt', 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(all_text))
        print("Content saved to pdf_content.txt")
    except ImportError:
        print("Neither pdfplumber nor PyPDF2 available")
        sys.exit(1)
