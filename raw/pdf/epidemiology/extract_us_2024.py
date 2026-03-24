import pymupdf
import json

pdf_path = "2024美国癌症预测报告（38页）.pdf"
doc = pymupdf.open(pdf_path)

print(f"Total pages: {len(doc)}")

# Extract all pages content for analysis
all_text = []
for i in range(len(doc)):
    page = doc[i]
    text = page.get_text()
    all_text.append(f"--- Page {i+1} ---\n{text}")

full_text = "\n".join(all_text)
with open("extracted_us_2024_38p.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print("\nExtracted all text to extracted_us_2024_38p.txt")
doc.close()
