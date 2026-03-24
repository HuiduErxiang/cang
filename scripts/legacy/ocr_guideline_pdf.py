# -*- coding: utf-8 -*-
import pdfplumber
import pytesseract
from PIL import Image
import io
import json

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025CSCO乳腺癌诊疗指南.pdf"

def ocr_page(page, page_num):
    """对PDF页面进行OCR"""
    # 将页面转换为图片
    im = page.to_image(resolution=200)
    # 获取PIL Image对象
    pil_img = im.original
    # OCR识别
    text = pytesseract.image_to_string(pil_img, lang='chi_sim+eng')
    return text

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    print(f"Total pages: {total_pages}")
    
    # OCR前30页获取基本信息和目录
    all_text = []
    for i in range(min(30, total_pages)):
        print(f"Processing page {i+1}...")
        page = pdf.pages[i]
        text = ocr_page(page, i+1)
        all_text.append({"page": i+1, "text": text})
        print(f"  Extracted {len(text)} characters")
    
    # 打印前10页的内容
    print("\n" + "="*60)
    for item in all_text[:10]:
        print(f"\n--- Page {item['page']} ---")
        print(item['text'][:800])
        print("-"*40)
