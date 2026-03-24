import fitz
import json
import io
from PIL import Image
import pytesseract

# Open the PDF file
pdf_path = "胃癌HER2检测指南(2016版).pdf"
doc = fitz.open(pdf_path)

print(f"Total pages: {len(doc)}")

# Extract text from all pages using different methods
full_text = ""
for i, page in enumerate(doc):
    print(f"\n--- Processing Page {i+1} ---")
    
    # Method 1: Try to get text directly
    text = page.get_text()
    
    # If text is garbled, try OCR on page as image
    if len(text.strip()) < 100 or any(ord(c) > 127 for c in text[:100]):
        print("Text appears garbled, using OCR...")
        # Render page to image
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        print(f"OCR extracted {len(text)} chars")
    else:
        print(f"Direct text extraction: {len(text)} chars")
    
    full_text += f"\n--- Page {i+1} ---\n{text}"

# Save extracted text
with open("pdf_extracted.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print("\n" + "="*50)
print("EXTRACTED CONTENT:")
print("="*50)
print(full_text)
