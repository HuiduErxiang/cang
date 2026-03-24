import json
import sys
import re
import fitz

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025 CSCO胃癌指南.pdf'
doc = fitz.open(pdf_path)

# 获取基本信息
total_pages = len(doc)
print(f"Total pages: {total_pages}", file=sys.stderr)

# 读取前几页获取标题信息
title_info = {
    'title': '2025 CSCO胃癌诊疗指南',
    'source': 'CSCO（中国临床肿瘤学会）/ 人民卫生出版社',
    'year': 2025,
    'issuing_body': 'CSCO（中国临床肿瘤学会）指南工作委员会'
}

# 扫描关键页面
key_pages_set = set()

# 扫描前20页 - 封面、前言、目录、推荐等级
for page_num in range(min(20, total_pages)):
    page = doc[page_num]
    text = page.get_text()
    
    if any(kw in text for kw in ['目录', '目次', 'Contents', '推荐等级', '证据类别', 'I级推荐', '本指南']):
        key_pages_set.add(page_num + 1)

# 扫描表格和图
all_tables = []
all_figures = []

for page_num in range(total_pages):
    page = doc[page_num]
    text = page.get_text()
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        # 查找表格
        if re.match(r'^表\s*[\d\-]+', line) or (line.startswith('表') and len(line) > 3 and len(line) < 100):
            if any(kw in line for kw in ['推荐', '分期', '治疗', '方案', '化疗', '靶向', '免疫', '病理', '诊断', '随访']):
                all_tables.append({
                    'id': line.split()[0] if ' ' in line else line[:10],
                    'title': line,
                    'page': page_num + 1
                })
                key_pages_set.add(page_num + 1)
        
        # 查找图
        if re.match(r'^图\s*[\d\-]+', line) or (line.startswith('图') and len(line) > 3 and len(line) < 80):
            all_figures.append({
                'id': line.split()[0] if ' ' in line else line[:10],
                'title': line,
                'page': page_num + 1
            })
            key_pages_set.add(page_num + 1)

# 提取胃癌相关的关键推荐
key_recommendations = []

# 常见的胃癌治疗方案关键词
treatment_keywords = [
    'XELOX', 'SOX', 'FOLFOX', 'DOS', 'ECF', 'DCF', 'XP', 'SP',
    '曲妥珠单抗', '帕博利珠单抗', '纳武利尤单抗', '信迪利单抗', '卡瑞利珠单抗',
    '雷莫西尤单抗', '阿帕替尼', '替吉奥', '卡培他滨', '奥沙利铂',
    'PD-1', 'PD-L1', 'HER2', 'MSI-H', 'dMMR', 'CPS', 'TPS',
    '新辅助化疗', '辅助化疗', '一线治疗', '二线治疗', '姑息治疗'
]

# 扫描治疗推荐相关页面
for page_num in range(20, min(total_pages - 20, total_pages)):
    page = doc[page_num]
    text = page.get_text()
    
    # 查找包含"推荐"和治疗关键词的内容
    if '推荐' in text:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # 过滤出包含治疗方案的推荐
            if any(kw in line for kw in treatment_keywords) and len(line) > 15 and len(line) < 300:
                # 排除页眉页脚和表格标题
                if not line.startswith('表') and not line.startswith('图') and not line.startswith('2025'):
                    if '推荐' in line or '方案' in line or '治疗' in line:
                        key_recommendations.append({
                            'content': line,
                            'page': page_num + 1
                        })
                        key_pages_set.add(page_num + 1)

# 去重推荐
seen_rec = set()
unique_recommendations = []
for rec in key_recommendations:
    content_key = rec['content'][:40]
    if content_key not in seen_rec:
        seen_rec.add(content_key)
        unique_recommendations.append(rec)

key_recommendations = unique_recommendations[:40]

# 去重表格
table_seen = set()
unique_tables = []
for t in all_tables:
    key = f"{t['title']}_{t['page']}"
    if key not in table_seen:
        table_seen.add(key)
        unique_tables.append(t)

# 按页码排序并选择关键表格
unique_tables.sort(key=lambda x: x['page'])
tables = unique_tables[:30]

# 去重图片
figure_seen = set()
unique_figures = []
for f in all_figures:
    key = f"{f['title']}_{f['page']}"
    if key not in figure_seen:
        figure_seen.add(key)
        unique_figures.append(f)

figures = unique_figures[:15]

# 构建关键页列表
key_pages = sorted(list(key_pages_set))[:25]

# 推荐强度定义
recommendation_strength = [
    {
        'level': 'I级推荐',
        'description': '证据类别高、可及性好的方案。适应证明确、可及性好、肿瘤治疗价值稳定，纳入《国家基本医疗保险、工伤保险和生育保险药品目录》的治疗方案',
        'page': 9
    },
    {
        'level': 'II级推荐',
        'description': '2A类证据。国内外随机对照研究提供高级别证据，但未纳入医保，或医保限制应用范围，或适应证明确、可及性好、肿瘤治疗价值稳定但纳入国家医保的适应证获批时间短的方案',
        'page': 9
    },
    {
        'level': 'III级推荐',
        'description': '证据类别不足，但专家组意见认为可以接受的方案',
        'page': 9
    }
]

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
    'disease_area': '胃癌（Gastric Cancer），包括胃腺癌、胃食管结合部癌',
    'target_population': '胃癌患者，涵盖可切除胃癌、不可切除局部晚期胃癌及转移性/复发性胃癌患者',
    'key_recommendations': key_recommendations,
    'recommendation_strength': recommendation_strength,
    'key_pages': key_pages,
    'figures': figures,
    'tables': tables
}

# 输出JSON
print(json.dumps(result, ensure_ascii=False, indent=2))
