import fitz  # PyMuPDF
import json

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025 CSCO胃癌指南.pdf"
doc = fitz.open(pdf_path)

print(f"PDF opened successfully")
print(f"Total pages: {len(doc)}")

# Get metadata
metadata = doc.metadata
print(f"\nMetadata:")
for key, value in metadata.items():
    if value:
        print(f"  {key}: {value}")

# Read first few pages to get title and basic info
print("\n" + "="*50)
print("First 5 pages content preview:")
for i in range(min(5, len(doc))):
    page = doc[i]
    text = page.get_text()
    print(f"\n--- Page {i+1} ---")
    print(text[:1500] if len(text) > 1500 else text)

# Read last few pages for references
print("\n" + "="*50)
print("Last 3 pages content preview:")
for i in range(max(0, len(doc)-3), len(doc)):
    page = doc[i]
    text = page.get_text()
    print(f"\n--- Page {i+1} ---")
    print(text[:1500] if len(text) > 1500 else text)

doc.close()
