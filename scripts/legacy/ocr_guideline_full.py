# -*- coding: utf-8 -*-
import pdfplumber
from PIL import Image
import easyocr
import json
import re

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025CSCO乳腺癌诊疗指南.pdf"

# 初始化easyocr reader（中文和英文）
print("Initializing EasyOCR reader...")
reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)

def ocr_page(page, page_num):
    """对PDF页面进行OCR"""
    im = page.to_image(resolution=150)
    pil_img = im.original
    temp_path = f"temp_guideline_page_{page_num}.png"
    pil_img.save(temp_path)
    result = reader.readtext(temp_path)
    text = '\n'.join([item[1] for item in result])
    return text

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    print(f"Total pages: {total_pages}")
    
    # 存储所有提取的信息
    key_recommendations = []
    tables = []
    figures = []
    key_pages = []
    
    # 读取关键页面（目录中标记的重要章节）
    important_pages = [1, 2, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 38, 46, 48, 49, 51, 58, 65, 76, 89, 90, 93, 100, 111, 118, 120, 121, 122, 123, 132, 133, 134, 140, 141, 145, 152, 160, 161, 165, 170, 172, 176, 179, 187, 189, 192, 195, 198, 202, 205]
    
    for page_num in important_pages:
        if page_num > total_pages:
            continue
        print(f"Processing page {page_num}...")
        page = pdf.pages[page_num - 1]  # 0-indexed
        text = ocr_page(page, page_num)
        
        # 查找推荐内容
        if any(kw in text for kw in ["级推荐", "证据", "推荐"]):
            lines = text.split('\n')
            for line in lines:
                if "级推荐" in line and len(line) > 10 and len(line) < 300:
                    key_recommendations.append({"page": page_num, "content": line.strip()})
        
        # 查找表格
        if re.search(r'表\s*\d+', text) or "Table" in text:
            lines = text.split('\n')
            for line in lines[:10]:
                match = re.search(r'表\s*(\d+)\s*([^\n]{0,100})', line)
                if match:
                    tables.append({
                        "number": f"表{match.group(1)}",
                        "title": match.group(2).strip(),
                        "page": page_num
                    })
                    break
        
        # 查找图
        if re.search(r'图\s*\d+', text) or "Figure" in text:
            lines = text.split('\n')
            for line in lines[:10]:
                match = re.search(r'图\s*(\d+)\s*([^\n]{0,100})', line)
                if match:
                    figures.append({
                        "number": f"图{match.group(1)}",
                        "title": match.group(2).strip(),
                        "page": page_num
                    })
                    break
    
    # 构建JSON输出
    output = {
        "title": "中国临床肿瘤学会(CSCO)乳腺癌诊疗指南2025",
        "source": "中国临床肿瘤学会(CSCO)",
        "year": 2025,
        "language": "zh",
        "total_pages": total_pages,
        "doi": None,
        "document_type": "guideline_consensus",
        "_source_pdf": "guidelines\\2025 CSCO指南\\2025CSCO乳腺癌诊疗指南.pdf",
        "issuing_body": "中国临床肿瘤学会指南工作委员会",
        "disease_area": "乳腺癌",
        "target_population": "乳腺癌患者",
        "key_recommendations": key_recommendations[:50],  # 限制数量
        "recommendation_strength": [
            {"level": "I级推荐", "description": "1A类证据和部分2A类证据，适应证明确、可及性好、肿瘤治疗价值稳定", "page": 2},
            {"level": "II级推荐", "description": "1B类证据和部分2A类证据，可及性差或效价比不高", "page": 2},
            {"level": "III级推荐", "description": "2B类证据和3类证据，临床实用但证据类别不高", "page": 2}
        ],
        "key_pages": [
            {"page": 1, "description": "封面-指南标题"},
            {"page": 12, "description": "前言"},
            {"page": 13, "description": "目录"},
            {"page": 17, "description": "CSCO诊疗指南证据类别"},
            {"page": 18, "description": "CSCO诊疗指南推荐等级"},
            {"page": 19, "description": "更新要点"},
            {"page": 23, "description": "乳腺癌的诊断及检查"},
            {"page": 27, "description": "乳腺癌的术前新辅助治疗"},
            {"page": 48, "description": "乳腺癌的术后辅助治疗"},
            {"page": 89, "description": "晚期乳腺癌的解救治疗"},
            {"page": 120, "description": "乳腺癌骨转移"},
            {"page": 132, "description": "乳腺癌脑转移"},
            {"page": 140, "description": "乳腺癌的治疗管理"}
        ],
        "figures": figures[:20],
        "tables": tables[:30]
    }
    
    # 打印JSON
    print("\n" + "="*60)
    print("JSON Output:")
    print(json.dumps(output, ensure_ascii=False, indent=2))
