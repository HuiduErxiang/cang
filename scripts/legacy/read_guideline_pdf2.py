# -*- coding: utf-8 -*-
import pdfplumber
import json

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025CSCO乳腺癌诊疗指南.pdf"

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    print(f"Total pages: {total_pages}")
    
    # 检查前10页的内容类型
    for i in range(min(10, total_pages)):
        page = pdf.pages[i]
        text = page.extract_text()
        images = page.images
        print(f"\nPage {i+1}:")
        print(f"  Text length: {len(text) if text else 0}")
        print(f"  Images count: {len(images)}")
        if text and len(text) > 0:
            print(f"  Text preview: {text[:300]}")
        else:
            print(f"  No text extracted - likely image/scanned page")
