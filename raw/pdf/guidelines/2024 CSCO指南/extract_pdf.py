import PyPDF2
import json
import re

pdf_path = "2024CSCO胃癌诊疗指南.pdf"

# Read PDF
with open(pdf_path, 'rb') as file:
    pdf_reader = PyPDF2.PdfReader(file)
    total_pages = len(pdf_reader.pages)
    print(f"Total pages: {total_pages}")
    
    # Extract text from all pages
    all_text = []
    for i in range(total_pages):
        page = pdf_reader.pages[i]
        text = page.extract_text()
        all_text.append(text)
    
    # Save all text for analysis
    with open("pdf_content.txt", "w", encoding="utf-8") as f:
        for i, text in enumerate(all_text):
            f.write(f"=== Page {i+1} ===\n")
            f.write(text)
            f.write("\n\n")
    
    print("PDF content extracted to pdf_content.txt")
    
    # Extract first 10 pages for initial analysis
    sample_text = "\n".join(all_text[:10])
    print("\n=== First 10 pages preview ===")
    print(sample_text[:5000])
