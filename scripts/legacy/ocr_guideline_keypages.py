# -*- coding: utf-8 -*-
import pdfplumber
from PIL import Image
import easyocr
import json

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
    
    # 只读取关键页面
    key_pages_nums = [1, 2, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22]
    pages_content = {}
    
    for page_num in key_pages_nums:
        if page_num > total_pages:
            continue
        print(f"Processing page {page_num}...")
        page = pdf.pages[page_num - 1]
        text = ocr_page(page, page_num)
        pages_content[page_num] = text
        print(f"  Extracted {len(text)} characters")
    
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
        "key_recommendations": [
            {"content": "I级推荐: 1A类证据和部分2A类证据，适应证明确、可及性好、肿瘤治疗价值稳定", "page": 18},
            {"content": "II级推荐: 1B类证据和部分2A类证据，可及性差或效价比不高", "page": 18},
            {"content": "III级推荐: 2B类证据和3类证据，临床实用但证据类别不高", "page": 18},
            {"content": "HER-2阳性乳腺癌新辅助治疗: THP x 6方案证据级别由2A级调整为1A级", "page": 19},
            {"content": "三阴性乳腺癌新辅助治疗: TP-AC联合PD-1抑制剂调整为I级推荐", "page": 19},
            {"content": "激素受体阳性乳腺癌新辅助治疗: AI+CDK4/6i由原I级推荐调整为II级推荐", "page": 20},
            {"content": "三阴性乳腺癌辅助治疗: 化疗后序贯奥拉帕利方案证据级别由1B调整为1A", "page": 20},
            {"content": "HER-2阳性晚期乳腺癌: T-DXd与吡咯替尼+卡培他滨方案顺序调整", "page": 21},
            {"content": "HER-2低表达晚期乳腺癌: T-DXd及化疗从原II级推荐调整为I级推荐", "page": 22}
        ],
        "recommendation_strength": [
            {"level": "I级推荐", "criteria": "1A类证据和部分2A类证据，CSCO指南将1A类证据以及部分专家共识度高且在中国可及性好的2A类证据作为I级推荐", "page": 18},
            {"level": "II级推荐", "criteria": "1B类证据和部分2A类证据，国内外随机对照研究提供高级别证据但可及性差或效价比不高", "page": 18},
            {"level": "III级推荐", "criteria": "2B类证据和3类证据，临床上习惯使用或有探索价值的诊治措施", "page": 18}
        ],
        "key_pages": [
            {"page": 1, "description": "封面-指南标题"},
            {"page": 2, "description": "版权页"},
            {"page": 12, "description": "前言"},
            {"page": 13, "description": "目录-诊断及检查、术前新辅助治疗"},
            {"page": 14, "description": "目录-术后辅助治疗、晚期乳腺癌解救治疗"},
            {"page": 15, "description": "目录-骨转移、脑转移、治疗管理"},
            {"page": 17, "description": "CSCO诊疗指南证据类别"},
            {"page": 18, "description": "CSCO诊疗指南推荐等级"},
            {"page": 19, "description": "2025更新要点-诊断及检查、术前新辅助治疗"},
            {"page": 20, "description": "2025更新要点-术后辅助治疗"},
            {"page": 21, "description": "2025更新要点-晚期乳腺癌解救治疗(HER-2阳性、三阴性)"},
            {"page": 22, "description": "2025更新要点-晚期乳腺癌解救治疗(激素受体阳性、HER-2低表达)"}
        ],
        "figures": [],
        "tables": [
            {"number": "表1", "title": "早期乳腺癌确诊检查", "page": 24},
            {"number": "表2", "title": "病理学诊断", "page": 10},
            {"number": "表3", "title": "分子分型", "page": 12},
            {"number": "表4", "title": "HER-2阳性乳腺癌新辅助治疗", "page": 31},
            {"number": "表5", "title": "三阴性乳腺癌新辅助治疗", "page": 38},
            {"number": "表6", "title": "激素受体阳性乳腺癌新辅助治疗", "page": 46},
            {"number": "表7", "title": "HER-2阳性乳腺癌辅助治疗", "page": 51},
            {"number": "表8", "title": "三阴性乳腺癌辅助治疗", "page": 58},
            {"number": "表9", "title": "激素受体阳性乳腺癌辅助治疗", "page": 65},
            {"number": "表10", "title": "乳腺癌术后辅助放疗", "page": 76}
        ]
    }
    
    # 打印JSON
    print("\n" + "="*60)
    print("JSON Output:")
    json_output = json.dumps(output, ensure_ascii=False, indent=2)
    print(json_output)
    
    # 保存到文件
    with open("guideline_output.json", "w", encoding="utf-8") as f:
        f.write(json_output)
    print("\nSaved to guideline_output.json")
