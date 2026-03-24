import fitz
from pdf2image import convert_from_path
import pytesseract
import json
import os

# Open the PDF file
pdf_path = "胃癌HER2检测指南(2016版).pdf"

# Convert PDF to images
print("Converting PDF to images...")
images = convert_from_path(pdf_path, dpi=300)
print(f"Converted {len(images)} pages")

# OCR each page
full_text = ""
for i, image in enumerate(images):
    print(f"OCR page {i+1}...")
    text = pytesseract.image_to_string(image, lang='chi_sim+eng')
    full_text += f"\n--- Page {i+1} ---\n{text}"

# Save extracted text
with open("pdf_ocr_content.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print("\n=== EXTRACTED CONTENT ===")
print(full_text)
