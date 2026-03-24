# -*- coding: utf-8 -*-
import pdfplumber
from PIL import Image
import easyocr
import json

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025CSCO乳腺癌诊疗指南.pdf"

# 初始化easyocr reader（中文和英文）
print("Initializing EasyOCR reader...")
reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    print(f"Total pages: {total_pages}")
    
    # OCR前25页获取基本信息和目录
    all_text = []
    for i in range(min(25, total_pages)):
        print(f"Processing page {i+1}...")
        page = pdf.pages[i]
        
        # 将页面转换为图片
        im = page.to_image(resolution=200)
        pil_img = im.original
        
        # 保存为临时文件
        temp_path = f"temp_page_{i+1}.png"
        pil_img.save(temp_path)
        
        # OCR识别
        result = reader.readtext(temp_path)
        text = '\n'.join([item[1] for item in result])
        
        all_text.append({"page": i+1, "text": text})
        print(f"  Extracted {len(text)} characters")
    
    # 打印内容
    print("\n" + "="*60)
    for item in all_text:
        print(f"\n--- Page {item['page']} ---")
        print(item['text'][:1000])
        print("-"*40)
