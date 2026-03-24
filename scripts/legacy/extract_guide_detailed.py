import json
import sys
import re
import fitz

doc = fitz.open(r'raw\pdf\guidelines\2024 CSCO指南\2024CSCO免疫检查点抑制剂临床应用指南.pdf')

result = {
    'title': '2024 CSCO免疫检查点抑制剂临床应用指南',
    'source': 'CSCO（中国临床肿瘤学会）/ 人民卫生出版社',
    'year': 2024,
    'language': 'zh-CN',
    'total_pages': len(doc),
    'doi': None,
    'document_type': 'guideline_consensus',
    '_source_pdf': r'guidelines\\2024 CSCO指南\\2024CSCO免疫检查点抑制剂临床应用指南.pdf',
    'issuing_body': 'CSCO（中国临床肿瘤学会）指南工作委员会',
    'disease_area': '肿瘤免疫治疗',
    'target_population': '接受免疫检查点抑制剂治疗的肿瘤患者',
    'key_recommendations': [],
    'recommendation_strength': [],
    'key_pages': [],
    'figures': [],
    'tables': []
}

# 扫描所有页面寻找关键内容
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    
    # 寻找推荐相关的内容 - 更精确的匹配
    if '级推荐' in text or '证据类别' in text:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if '级推荐' in line and len(line) < 300:
                # 去重检查
                is_duplicate = False
                for rec in result['key_recommendations']:
                    if line[:50] in rec['content'] or rec['content'][:50] in line:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    result['key_recommendations'].append({
                        'content': line,
                        'page': page_num + 1
                    })
    
    # 寻找表格 - 匹配模式如 "表1", "表 1", "表2-1" 等
    table_matches = re.findall(r'(表\s*[\d\-]+[\s\.]*[^\n]{0,100})', text)
    for match in table_matches:
        match = match.strip()
        if len(match) > 3 and len(match) < 150:
            is_duplicate = False
            for t in result['tables']:
                if match[:30] in t['title']:
                    is_duplicate = True
                    break
            if not is_duplicate:
                result['tables'].append({
                    'id': match.split()[0] if ' ' in match else match[:10],
                    'title': match,
                    'page': page_num + 1
                })
    
    # 寻找图 - 匹配模式如 "图1", "图 1", "图2-1" 等
    figure_matches = re.findall(r'(图\s*[\d\-]+[\s\.]*[^\n]{0,100})', text)
    for match in figure_matches:
        match = match.strip()
        if len(match) > 3 and len(match) < 150:
            is_duplicate = False
            for f in result['figures']:
                if match[:30] in f['title']:
                    is_duplicate = True
                    break
            if not is_duplicate:
                result['figures'].append({
                    'id': match.split()[0] if ' ' in match else match[:10],
                    'title': match,
                    'page': page_num + 1
                })

# 限制数量
result['key_recommendations'] = result['key_recommendations'][:60]
result['tables'] = result['tables'][:30]
result['figures'] = result['figures'][:20]

# 添加关键页码
result['key_pages'] = [1, 9, 10, 13, 14, 15, 16, 17, 18, 19, 20]

doc.close()

# 输出JSON
print(json.dumps(result, ensure_ascii=False, indent=2))
