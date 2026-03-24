import pymupdf
import json

pdf_path = "2022年中国恶性肿瘤流行情况分析.pdf"
doc = pymupdf.open(pdf_path)

print(f"Total pages: {len(doc)}")

# Extract text from first few pages to understand structure
for i in range(min(5, len(doc))):
    page = doc[i]
    text = page.get_text()
    print(f"\n=== Page {i+1} ===")
    print(text[:2000])

# Extract all pages content for analysis
all_text = []
for i in range(len(doc)):
    page = doc[i]
    text = page.get_text()
    all_text.append(f"--- Page {i+1} ---\n{text}")

full_text = "\n".join(all_text)
with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print("\n\nExtracted all text to extracted_text.txt")
doc.close()
