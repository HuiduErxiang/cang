# -*- coding: utf-8 -*-
import fitz  # PyMuPDF
import json
import os

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\oncology\lung_cancer\SCLC\CASPIAN研究补充资料.pdf"

def extract_pdf_content(pdf_path):
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    # 提取所有页面的文本
    all_text = []
    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text()
        all_text.append({
            "page": page_num + 1,
            "text": text
        })
    
    doc.close()
    return {
        "total_pages": total_pages,
        "pages": all_text
    }

result = extract_pdf_content(pdf_path)
print(json.dumps(result, ensure_ascii=False, indent=2))
