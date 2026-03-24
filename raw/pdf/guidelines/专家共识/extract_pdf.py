import fitz
import json
import re

# Open the PDF file
pdf_path = "胃癌HER2检测指南(2016版).pdf"
doc = fitz.open(pdf_path)

# Get basic info
total_pages = len(doc)
print("Total pages:", total_pages)

# Extract text from all pages
full_text = ""
for i, page in enumerate(doc):
    text = page.get_text()
    full_text += "\n--- Page " + str(i+1) + " ---\n" + text

# Save full text for analysis
with open("temp_pdf_content.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print("Full text extracted")
print(full_text[:8000])
