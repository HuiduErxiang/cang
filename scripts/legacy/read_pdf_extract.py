import pdfplumber
import json
import re

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\oncology\prostate_cancer\TheraP研究.pdf"

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    print(f"Total pages: {total_pages}")
    
    # Extract text from all pages
    all_text = []
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            all_text.append(f"=== Page {i+1} ===\n{text}")
    
    full_text = "\n\n".join(all_text)
    
    # Save full text for analysis
    with open("therap_extracted.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    
    print("Text extraction complete. Saved to therap_extracted.txt")
    print("\nFirst 5000 characters preview:")
    print(full_text[:5000])
