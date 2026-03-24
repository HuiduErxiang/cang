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
    '_source_pdf': r'guidelines\2024 CSCO指南\2024CSCO免疫检查点抑制剂临床应用指南.pdf',
    'issuing_body': 'CSCO（中国临床肿瘤学会）指南工作委员会',
    'disease_area': '肿瘤免疫治疗（涵盖鼻咽癌、食管癌、肺癌、乳腺癌、胃癌、肝癌、胆道肿瘤、胰腺癌、结直肠癌、肾癌、尿路上皮癌、宫颈癌、卵巢癌、黑色素瘤、淋巴瘤、皮肤肿瘤等）',
    'target_population': '接受免疫检查点抑制剂治疗的肿瘤患者',
    'key_recommendations': [],
    'recommendation_strength': [
        {
            'level': 'I级推荐',
            'description': '证据类别高、可及性好的方案。具体为：适应证明确、可及性好、肿瘤治疗价值稳定，纳入《国家基本医疗保险、工伤保险和生育保险药品目录》的免疫检查点抑制剂治疗方案',
            'page': 13
        },
        {
            'level': 'II级推荐',
            'description': '2A类证据。具体为：国内外随机对照研究，提供高级别证据，但未纳入医保，或医保限制应用范围，或适应证明确、可及性好、肿瘤治疗价值稳定，但纳入国家医保的适应证获批时间短、专家组投票认为临床明确能获益的方案',
            'page': 13
        },
        {
            'level': 'III级推荐',
            'description': '证据类别不足，但专家组意见认为可以接受的方案',
            'page': 13
        }
    ],
    'key_pages': [1, 9, 10, 13, 14, 15, 16, 17, 18, 19, 20],
    'figures': [],
    'tables': []
}

# 从更新要点中提取关键推荐（基于2024版更新内容）
key_updates = [
    {'content': '新增"舒格利单抗+顺铂+5-FU"为鼻咽癌晚期一线治疗I级推荐', 'page': 14},
    {'content': '新增"特瑞普利单抗+含铂化疗新辅助+辅助治疗"为食管癌围手术期治疗I级推荐', 'page': 14},
    {'content': '将"信迪利单抗+贝伐珠单抗类似物+化疗"升级为肝癌晚期二线及以上治疗I级推荐', 'page': 15},
    {'content': '新增"斯鲁利单抗+白蛋白紫杉醇+卡铂"为肺癌晚期一线治疗I级推荐', 'page': 15},
    {'content': '新增"帕博利珠单抗+培美曲塞+顺铂/卡铂"为恶性胸膜间皮瘤一线治疗I级推荐', 'page': 16},
    {'content': '新增"特瑞普利单抗+白蛋白紫杉醇"为三阴性乳腺癌晚期一线治疗II级推荐', 'page': 16},
    {'content': '新增"阿替利珠单抗+贝伐珠单抗"为肝细胞癌术后辅助治疗I级推荐', 'page': 17},
    {'content': '新增"吉西他滨+顺铂+帕博利珠单抗"为胆道肿瘤一线治疗I级推荐', 'page': 17},
    {'content': '新增"特瑞普利单抗+阿昔替尼"为肾透明细胞癌晚期一线治疗I级推荐', 'page': 18},
    {'content': '新增"纳武利尤单抗+吉西他滨+顺铂"为尿路上皮癌晚期一线治疗I级推荐', 'page': 18},
    {'content': '将"阿维鲁单抗"升级为尿路上皮癌维持治疗I级推荐', 'page': 19},
    {'content': '新增"帕博利珠单抗+卡铂+紫杉醇"为宫颈癌一线治疗I级推荐', 'page': 19},
    {'content': '新增"替雷利珠单抗"和"斯鲁利单抗"为dMMR/MSI-H胃癌二线治疗I级推荐', 'page': 17},
    {'content': '新增"舒格利单抗"为结外NK/T细胞淋巴瘤I级推荐', 'page': 20},
]

result['key_recommendations'] = key_updates

# 扫描页面寻找表格和图
for page_num in range(30, min(150, len(doc)), 10):  # 扫描部分页面
    page = doc[page_num]
    text = page.get_text()
    
    # 寻找表格标题
    lines = text.split('\n')
    for i, line in enumerate(lines[:30]):
        line = line.strip()
        # 表格模式
        if re.match(r'^表[\s]*[\d\-]+', line) and len(line) < 120:
            is_dup = False
            for t in result['tables']:
                if line[:40] == t['title'][:40]:
                    is_dup = True
                    break
            if not is_dup:
                result['tables'].append({
                    'id': line.split()[0] if line.split() else f'表_{page_num}',
                    'title': line,
                    'page': page_num + 1
                })
        # 图模式
        if re.match(r'^图[\s]*[\d\-]+', line) and len(line) < 120:
            is_dup = False
            for f in result['figures']:
                if line[:40] == f['title'][:40]:
                    is_dup = True
                    break
            if not is_dup:
                result['figures'].append({
                    'id': line.split()[0] if line.split() else f'图_{page_num}',
                    'title': line,
                    'page': page_num + 1
                })

# 扫描附录中的表格
for page_num in range(240, min(256, len(doc))):
    page = doc[page_num]
    text = page.get_text()
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if ('表' in line or 'Table' in line or 'TABLE' in line) and len(line) < 150 and len(line) > 5:
            # 检查是否包含数字
            if any(c.isdigit() for c in line):
                is_dup = False
                for t in result['tables']:
                    if line[:40] == t['title'][:40]:
                        is_dup = True
                        break
                if not is_dup:
                    result['tables'].append({
                        'id': line.split()[0] if line.split() else f'附录_{page_num}',
                        'title': line,
                        'page': page_num + 1
                    })

doc.close()

# 限制表格和图数量
result['tables'] = result['tables'][:25]
result['figures'] = result['figures'][:15]

# 输出JSON
print(json.dumps(result, ensure_ascii=False, indent=2))
