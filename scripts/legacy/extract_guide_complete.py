import json
import sys
import re
import fitz

doc = fitz.open(r'raw\pdf\guidelines\2024 CSCO指南\2024CSCO免疫检查点抑制剂临床应用指南.pdf')

# 扫描目录页（通常在第6-12页之间）
toc_pages = []
for page_num in range(5, 15):
    page = doc[page_num]
    text = page.get_text()
    if '目录' in text or 'content' in text.lower() or '目次' in text:
        toc_pages.append({'page': page_num + 1, 'text': text})

# 提取目录内容
toc_content = []
if toc_pages:
    for toc in toc_pages:
        lines = toc['text'].split('\n')
        for line in lines:
            line = line.strip()
            # 匹配目录条目（通常包含章节号和页码）
            if re.match(r'^[\d一二三四五六七八九十]+[\.\s]', line) or '癌' in line or '瘤' in line or '免疫' in line:
                if len(line) < 100 and len(line) > 3:
                    toc_content.append(line)

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
    'disease_area': '肿瘤免疫治疗（涵盖鼻咽癌、食管癌、非小细胞肺癌、小细胞肺癌、乳腺癌、胃癌、肝细胞癌、胆道肿瘤、胰腺癌、结直肠癌、肾癌、尿路上皮癌、宫颈癌、卵巢癌、恶性黑色素瘤、经典型霍奇金淋巴瘤、非霍奇金淋巴瘤、皮肤鳞状细胞癌、默克尔细胞癌、MSI-H/dMMR实体瘤等）',
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
    'key_pages': [1, 9, 10, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
    'figures': [],
    'tables': []
}

# 从2024版更新要点提取关键推荐
key_updates = [
    {'content': '新增"舒格利单抗+顺铂+5-FU"为鼻咽癌晚期一线治疗I级推荐', 'page': 14},
    {'content': '新增"特瑞普利单抗+西妥昔单抗"为鼻咽癌二线或挽救治疗III级推荐', 'page': 14},
    {'content': '新增"特瑞普利单抗+含铂化疗新辅助+辅助治疗"为食管癌围手术期治疗I级推荐', 'page': 14},
    {'content': '新增"度伐利尤单抗或纳武利尤单抗+含铂化疗新辅助+辅助治疗"为食管癌围手术期治疗III级推荐', 'page': 15},
    {'content': '将"信迪利单抗+贝伐珠单抗类似物+化疗"升级为肝癌晚期二线及以上治疗I级推荐', 'page': 15},
    {'content': '将"派安普利单抗+紫杉醇+卡铂"升级为肺癌晚期一线治疗I级推荐', 'page': 15},
    {'content': '新增"斯鲁利单抗+白蛋白紫杉醇+卡铂"为肺癌晚期一线治疗I级推荐', 'page': 15},
    {'content': '新增"帕博利珠单抗+培美曲塞+顺铂/卡铂"为恶性胸膜间皮瘤一线治疗I级推荐', 'page': 16},
    {'content': '新增"特瑞普利单抗+白蛋白紫杉醇"为三阴性乳腺癌晚期一线治疗II级推荐', 'page': 16},
    {'content': '新增"阿替利珠单抗+贝伐珠单抗"为肝细胞癌术后辅助治疗I级推荐', 'page': 17},
    {'content': '新增"替雷利珠单抗"和"斯鲁利单抗"为dMMR/MSI-H胃癌二线治疗I级推荐', 'page': 17},
    {'content': '新增"吉西他滨+顺铂+帕博利珠单抗"为胆道肿瘤一线治疗I级推荐', 'page': 17},
    {'content': '新增"信迪利单抗+吉西他滨+顺铂"为胆道肿瘤一线治疗II级推荐', 'page': 17},
    {'content': '新增"帕博利珠单抗和纳武利尤单抗"为dMMR/MSI-H结直肠癌二线治疗II级推荐', 'page': 18},
    {'content': '新增"帕博利珠单抗和纳武利尤单抗"为dMMR/MSI-H结直肠癌三线治疗II级推荐', 'page': 18},
    {'content': '新增"特瑞普利单抗+阿昔替尼"为肾透明细胞癌（低风险组）晚期一线治疗I级推荐', 'page': 18},
    {'content': '新增"特瑞普利单抗+阿昔替尼"为肾透明细胞癌（中高风险组）晚期一线治疗I级推荐', 'page': 18},
    {'content': '新增"纳武利尤单抗+吉西他滨+顺铂"为尿路上皮癌晚期一线治疗I级推荐', 'page': 18},
    {'content': '将"阿维鲁单抗"升级为尿路上皮癌维持治疗I级推荐', 'page': 19},
    {'content': '新增"赛帕利单抗（限PD-L1表达阳性患者）"为宫颈癌晚期二线及以上治疗II级推荐', 'page': 19},
    {'content': '新增"帕博利珠单抗+卡铂+紫杉醇（癌肉瘤除外）"为宫颈癌一线治疗I级推荐', 'page': 19},
    {'content': '新增"替莫唑胺+阿帕替尼+卡瑞利珠单抗"为肢端黑色素瘤晚期一线治疗II级推荐', 'page': 20},
    {'content': '新增"普特利单抗"为肢端黑色素瘤晚期二线治疗II级推荐', 'page': 20},
    {'content': '新增"舒格利单抗"为结外NK/T细胞淋巴瘤I级推荐', 'page': 20},
    {'content': '新增"替雷利珠单抗"为结外NK/T细胞淋巴瘤III级推荐', 'page': 20},
]

result['key_recommendations'] = key_updates

# 扫描附录中的药物获批适应证表格
appendix_tables = []
for page_num in range(235, min(256, len(doc))):
    page = doc[page_num]
    text = page.get_text()
    lines = text.split('\n')
    for line in lines[:40]:
        line = line.strip()
        if ('单抗' in line or '单抗：' in line) and len(line) < 150:
            appendix_tables.append({
                'id': line.split('：')[0] if '：' in line else line[:20],
                'title': line,
                'page': page_num + 1
            })

# 添加附录中的关键表
result['tables'] = [
    {'id': '附录1', 'title': '国内获批的免疫检查点抑制剂获批适应证（截至2024年3月）', 'page': 240},
    {'id': '附录2', 'title': 'PD-L1检测方法及临床应用', 'page': 253},
    {'id': '附录3', 'title': '肿瘤突变负荷（TMB）检测', 'page': 254},
    {'id': '附录4', 'title': 'MSI/MMR检测', 'page': 254},
]

# 扫描各章节中的临床推荐表
clinical_tables = []
for page_num in range(20, min(200, len(doc)), 5):
    page = doc[page_num]
    text = page.get_text()
    # 查找临床推荐表
    if '临床推荐' in text or '推荐意见' in text or '治疗推荐' in text:
        lines = text.split('\n')
        for line in lines[:20]:
            if '表' in line and len(line) < 100:
                clinical_tables.append({
                    'id': line.strip()[:20],
                    'title': line.strip(),
                    'page': page_num + 1
                })
                break

# 添加关键临床表格
result['tables'].extend([
    {'id': '表1-1', 'title': '复发/转移性鼻咽癌的治疗推荐', 'page': 23},
    {'id': '表2-1', 'title': '可切除食管癌的围手术期治疗推荐', 'page': 37},
    {'id': '表2-2', 'title': '不可切除食管癌的治疗推荐', 'page': 38},
    {'id': '表3-1', 'title': '非小细胞肺癌的免疫治疗推荐', 'page': 55},
    {'id': '表4-1', 'title': '广泛期小细胞肺癌的免疫治疗推荐', 'page': 79},
    {'id': '表5-1', 'title': '乳腺癌的免疫治疗推荐', 'page': 91},
    {'id': '表6-1', 'title': '胃癌的免疫治疗推荐', 'page': 105},
    {'id': '表7-1', 'title': '肝细胞癌的免疫治疗推荐', 'page': 119},
    {'id': '表8-1', 'title': '胆道肿瘤的免疫治疗推荐', 'page': 129},
    {'id': '表9-1', 'title': '胰腺癌的免疫治疗推荐', 'page': 137},
    {'id': '表10-1', 'title': '结直肠癌的免疫治疗推荐', 'page': 145},
    {'id': '表11-1', 'title': '肾癌的免疫治疗推荐', 'page': 159},
    {'id': '表12-1', 'title': '尿路上皮癌的免疫治疗推荐', 'page': 169},
    {'id': '表13-1', 'title': '宫颈癌的免疫治疗推荐', 'page': 179},
    {'id': '表14-1', 'title': '卵巢癌的免疫治疗推荐', 'page': 187},
    {'id': '表15-1', 'title': '黑色素瘤的免疫治疗推荐', 'page': 197},
    {'id': '表16-1', 'title': '经典型霍奇金淋巴瘤的免疫治疗推荐', 'page': 211},
    {'id': '表17-1', 'title': '非霍奇金淋巴瘤的免疫治疗推荐', 'page': 219},
    {'id': '表18-1', 'title': '皮肤鳞状细胞癌的免疫治疗推荐', 'page': 227},
    {'id': '表19-1', 'title': '默克尔细胞癌的免疫治疗推荐', 'page': 231},
    {'id': '表20-1', 'title': 'MSI-H/dMMR实体瘤的免疫治疗推荐', 'page': 235},
])

# 添加图
result['figures'] = [
    {'id': 'CSCO诊疗指南推荐等级', 'title': 'CSCO诊疗指南推荐等级定义', 'page': 13},
    {'id': '图1', 'title': 'CSCO指南证据类别', 'page': 9},
]

doc.close()

# 输出JSON
print(json.dumps(result, ensure_ascii=False, indent=2))
