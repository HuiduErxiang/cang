import fitz  # PyMuPDF
import sys

pdf_path = "中国去势抵抗性前列腺癌诊治专家共识.pdf"

doc = fitz.open(pdf_path)
total_pages = len(doc)
print(f"Total pages: {total_pages}")

for page_num in range(total_pages):
    page = doc[page_num]
    print(f"\n--- Page {page_num+1} ---")
    text = page.get_text()
    print(text[:3000])

doc.close()
