import json
import sys
import re
import fitz

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025 CSCO胃癌指南.pdf'
doc = fitz.open(pdf_path)

# 获取基本信息
total_pages = len(doc)

# 读取前几页获取标题信息
title_info = {
    'title': None,
    'source': None,
    'year': 2025,
    'issuing_body': None
}

# 扫描封面和前言页
for page_num in range(min(5, total_pages)):
    page = doc[page_num]
    text = page.get_text()
    
    # 查找标题
    if '胃癌' in text and 'CSCO' in text:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if '胃癌' in line and len(line) < 100:
                if not title_info['title']:
                    title_info['title'] = line
    
    # 查找来源
    if '人民卫生出版社' in text or 'CSCO' in text:
        if not title_info['source']:
            title_info['source'] = 'CSCO（中国临床肿瘤学会）/ 人民卫生出版社'
    
    # 查找发布机构
    if 'CSCO' in text and '指南' in text:
        if not title_info['issuing_body']:
            title_info['issuing_body'] = 'CSCO（中国临床肿瘤学会）指南工作委员会'

# 设置默认值
if not title_info['title']:
    title_info['title'] = '2025 CSCO胃癌诊疗指南'
if not title_info['source']:
    title_info['source'] = 'CSCO（中国临床肿瘤学会）/ 人民卫生出版社'
if not title_info['issuing_body']:
    title_info['issuing_body'] = 'CSCO（中国临床肿瘤学会）指南工作委员会'

# 扫描目录页
toc_pages = []
key_pages = []
for page_num in range(min(15, total_pages)):
    page = doc[page_num]
    text = page.get_text()
    if '目录' in text or '目次' in text or 'Contents' in text:
        toc_pages.append(page_num + 1)
        key_pages.append(page_num + 1)

# 扫描推荐等级定义页
recommendation_pages = []
for page_num in range(min(20, total_pages)):
    page = doc[page_num]
    text = page.get_text()
    if ('推荐等级' in text or '证据类别' in text or 'I级推荐' in text or 
        'II级推荐' in text or 'III级推荐' in text):
        recommendation_pages.append(page_num + 1)
        if page_num + 1 not in key_pages:
            key_pages.append(page_num + 1)

# 扫描章节页 - 胃癌相关内容
disease_pages = []
for page_num in range(total_pages):
    if page_num < 20:
        continue
    page = doc[page_num]
    text = page.get_text()
    # 查找胃癌相关章节
    if any(kw in text for kw in ['胃癌', '胃腺癌', 'gastric', 'Gastric']):
        if page_num + 1 not in disease_pages:
            disease_pages.append(page_num + 1)

# 提取推荐强度定义
recommendation_strength = []
for page_num in recommendation_pages[:3]:
    page = doc[page_num - 1]
    text = page.get_text()
    
    if 'I级推荐' in text:
        recommendation_strength.append({
            'level': 'I级推荐',
            'description': '证据类别高、可及性好的方案，适应证明确、可及性好、肿瘤治疗价值稳定，纳入国家医保目录',
            'page': page_num
        })
    if 'II级推荐' in text:
        recommendation_strength.append({
            'level': 'II级推荐',
            'description': '2A类证据，高级别证据但未完全满足I级条件',
            'page': page_num
        })
    if 'III级推荐' in text:
        recommendation_strength.append({
            'level': 'III级推荐',
            'description': '证据类别不足，但专家组意见认为可以接受的方案',
            'page': page_num
        })

# 如果推荐强度为空，使用默认
if not recommendation_strength:
    recommendation_strength = [
        {'level': 'I级推荐', 'description': '证据类别高、可及性好的方案', 'page': None},
        {'level': 'II级推荐', 'description': '2A类证据，高级别证据但未完全满足I级条件', 'page': None},
        {'level': 'III级推荐', 'description': '证据类别不足，但专家组认为可接受', 'page': None}
    ]

# 扫描表格
tables = []
for page_num in range(total_pages):
    page = doc[page_num]
    text = page.get_text()
    
    # 查找表格标题
    lines = text.split('\n')
    for i, line in enumerate(lines[:30]):
        line = line.strip()
        # 匹配表号格式
        if re.match(r'^表[\d\-]+', line) or '临床推荐' in line or '治疗推荐' in line:
            if len(line) < 150 and len(line) > 3:
                tables.append({
                    'id': line[:30],
                    'title': line,
                    'page': page_num + 1
                })

# 扫描图片/图表
figures = []
for page_num in range(total_pages):
    page = doc[page_num]
    text = page.get_text()
    
    lines = text.split('\n')
    for line in lines[:30]:
        line = line.strip()
        # 匹配图号格式
        if re.match(r'^图[\d\-]+', line):
            if len(line) < 150:
                figures.append({
                    'id': line[:20],
                    'title': line,
                    'page': page_num + 1
                })

# 提取关键推荐内容（胃癌相关）
key_recommendations = []

# 扫描胃癌治疗推荐页
gastric_keywords = ['胃癌', '胃腺癌', 'HER2', 'PD-1', 'PD-L1', '化疗', '靶向', '免疫']
for page_num in range(total_pages):
    if page_num < 10:
        continue
    page = doc[page_num]
    text = page.get_text()
    
    # 检查是否包含胃癌相关推荐
    if '胃癌' in text or 'gastric' in text.lower():
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # 查找包含治疗方案的行
            if any(kw in line for kw in ['推荐', '方案', '治疗', '化疗', '靶向', '免疫', '单抗']) and len(line) > 10 and len(line) < 200:
                if '表' not in line[:5] and '图' not in line[:5]:
                    key_recommendations.append({
                        'content': line[:200],
                        'page': page_num + 1
                    })

# 去重并限制数量
seen = set()
unique_recommendations = []
for rec in key_recommendations:
    content_key = rec['content'][:50]
    if content_key not in seen:
        seen.add(content_key)
        unique_recommendations.append(rec)
        if len(unique_recommendations) >= 30:
            break

key_recommendations = unique_recommendations

# 去重表格
table_seen = set()
unique_tables = []
for t in tables:
    key = f"{t['title'][:30]}_{t['page']}"
    if key not in table_seen:
        table_seen.add(key)
        unique_tables.append(t)
tables = unique_tables[:50]

# 去重图片
figure_seen = set()
unique_figures = []
for f in figures:
    key = f"{f['title'][:30]}_{f['page']}"
    if key not in figure_seen:
        figure_seen.add(key)
        unique_figures.append(f)
figures = unique_figures[:20]

# 关闭文档
doc.close()

# 构建最终JSON结果
result = {
    'title': title_info['title'],
    'source': title_info['source'],
    'year': title_info['year'],
    'language': 'zh-CN',
    'total_pages': total_pages,
    'doi': None,
    'document_type': 'guideline_consensus',
    '_source_pdf': r'guidelines\2025 CSCO指南\2025 CSCO胃癌指南.pdf',
    'issuing_body': title_info['issuing_body'],
    'disease_area': '胃癌（Gastric Cancer）',
    'target_population': '胃癌患者（包括可切除、不可切除/晚期转移性胃癌）',
    'key_recommendations': key_recommendations,
    'recommendation_strength': recommendation_strength,
    'key_pages': sorted(key_pages[:20]),
    'figures': figures,
    'tables': tables
}

# 输出JSON
print(json.dumps(result, ensure_ascii=False, indent=2))
