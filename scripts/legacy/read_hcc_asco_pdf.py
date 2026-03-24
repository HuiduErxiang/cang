import fitz  # PyMuPDF
import json
import sys

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\conferences\2025_asco_gi\2025 ASCO GI 会议幻灯集锦（中文版）-恒瑞医学\2025 ASCO GI 肝癌领域研究进展-恒瑞医学.pdf"

doc = fitz.open(pdf_path)

print(f"Total pages: {len(doc)}")
print("=" * 50)

# Extract text from each page
all_text = []
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    all_text.append({
        "page": page_num + 1,
        "text": text
    })
    print(f"\n--- Page {page_num + 1} ---")
    print(text[:3000] if len(text) > 3000 else text)

# Save full text for analysis
with open("temp_hcc_asco_text.json", "w", encoding="utf-8") as f:
    json.dump(all_text, f, ensure_ascii=False, indent=2)

doc.close()
