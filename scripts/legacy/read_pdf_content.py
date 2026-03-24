import fitz
import sys

doc = fitz.open(r'raw\pdf\conferences\2025_asco_gi\2025 ASCO GI 会议幻灯集锦（中文版）-恒瑞医学\2025 ASCO GI 胰腺癌领域研究进展-恒瑞医学.pdf')

with open('temp_pdf_output.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total pages: {len(doc)}\n")
    f.write("="*50 + "\n")
    
    for i in range(len(doc)):
        text = doc[i].get_text()
        if text.strip():
            f.write(f"\n=== PAGE {i+1} ===\n")
            f.write(text)
            f.write("\n")

print("Done! Output written to temp_pdf_output.txt")
