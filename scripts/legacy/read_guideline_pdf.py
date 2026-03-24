# -*- coding: utf-8 -*-
import pdfplumber
import json
import re

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025CSCO乳腺癌诊疗指南.pdf"

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    print(f"Total pages: {total_pages}")
    
    # 读取前几页获取基本信息
    first_page_text = pdf.pages[0].extract_text() if total_pages > 0 else ""
    print("="*50)
    print("Page 1 content:")
    print(first_page_text[:2000] if first_page_text else "None")
    
    # 尝试读取更多页获取目录和推荐
    toc_pages = []
    key_pages = []
    
    # 读取前20页获取标题页和目录
    for i in range(min(20, total_pages)):
        text = pdf.pages[i].extract_text()
        if text:
            # 查找目录页
            if "目录" in text or "Contents" in text or "CSCO" in text:
                toc_pages.append({"page": i+1, "text": text[:1000]})
            # 查找关键推荐
            if any(kw in text for kw in ["推荐", "证据", "级别", "推荐等级"]):
                key_pages.append({"page": i+1, "preview": text[:500]})
    
    print("\n" + "="*50)
    print("TOC pages found:", len(toc_pages))
    for tp in toc_pages[:3]:
        print(f"Page {tp['page']}: {tp['text'][:300]}...")
    
    # 搜索特定章节
    print("\n" + "="*50)
    print("Searching for key sections...")
    
    # 查找乳腺癌相关内容和推荐
    sections = []
    for i in range(min(100, total_pages)):
        text = pdf.pages[i].extract_text()
        if text:
            # 查找章节标题
            lines = text.split('\n')
            for line in lines[:10]:
                if re.search(r'^(\d+|[一二三四五六七八九十]+)[\.、\s]', line.strip()):
                    sections.append({"page": i+1, "title": line.strip()})
                    break
    
    print(f"Found {len(sections)} sections")
    for s in sections[:10]:
        print(f"  Page {s['page']}: {s['title']}")
    
    # 查找推荐内容和表格
    recommendations = []
    tables_info = []
    figures_info = []
    
    for i in range(total_pages):
        text = pdf.pages[i].extract_text()
        if not text:
            continue
            
        # 查找推荐
        if "推荐" in text and ("证据" in text or "级别" in text or "Grade" in text):
            lines = text.split('\n')
            for line in lines:
                if "推荐" in line and len(line) < 200:
                    recommendations.append({"page": i+1, "content": line.strip()})
        
        # 查找表格
        if "表" in text or "Table" in text:
            lines = text.split('\n')
            for line in lines[:5]:
                if re.search(r'表\s*\d+|Table\s*\d+', line):
                    tables_info.append({"page": i+1, "title": line.strip()})
                    break
        
        # 查找图
        if "图" in text or "Figure" in text:
            lines = text.split('\n')
            for line in lines[:5]:
                if re.search(r'图\s*\d+|Figure\s*\d+', line):
                    figures_info.append({"page": i+1, "title": line.strip()})
                    break
    
    print("\n" + "="*50)
    print(f"Found {len(recommendations)} recommendations")
    for r in recommendations[:5]:
        print(f"  Page {r['page']}: {r['content'][:100]}...")
    
    print("\n" + "="*50)
    print(f"Found {len(tables_info)} tables")
    for t in tables_info[:5]:
        print(f"  Page {t['page']}: {t['title']}")
    
    print("\n" + "="*50)
    print(f"Found {len(figures_info)} figures")
    for f in figures_info[:5]:
        print(f"  Page {f['page']}: {f['title']}")
