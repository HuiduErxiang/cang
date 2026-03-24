import fitz
import json
import re

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2026\中国抗癌协会乳腺癌诊治指南与规范（2026年版）.pdf'
doc = fitz.open(pdf_path)

total_pages = len(doc)

# 提取关键推荐意见
key_recommendations = []
key_pages = []
figures = []
tables = []

# 扫描所有页面提取信息
for page_idx in range(total_pages):
    page = doc[page_idx]
    text = page.get_text()
    page_num = page_idx + 1
    
    # 查找推荐（带编号的段落）
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if len(line) > 15:
            # 匹配中文编号格式
            if re.match(r'^[⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽①②③④⑤⑥⑦⑧⑨⑩]', line):
                key_recommendations.append({
                    'content': line[:300],
                    'page': page_num
                })
    
    # 查找表格引用
    table_refs = re.findall(r'(表\s*\d+[\-\.]?\d*\s*[:：][^\n]{0,80})', text)
    for ref in table_refs:
        tables.append({
            'id': ref.split('：')[0].strip() if '：' in ref else ref[:15].strip(),
            'description': ref.strip(),
            'page': page_num
        })
    
    # 查找图引用
    fig_refs = re.findall(r'(图\s*\d+[\-\.]?\d*\s*[:：][^\n]{0,80})', text)
    for ref in fig_refs:
        figures.append({
            'id': ref.split('：')[0].strip() if '：' in ref else ref[:15].strip(),
            'description': ref.strip(),
            'page': page_num
        })

doc.close()

# 去重
tables = list({t['id']: t for t in tables}.values())
figures = list({f['id']: f for f in figures}.values())

print(f"Total pages: {total_pages}")
print(f"Recommendations found: {len(key_recommendations)}")
print(f"Tables found: {len(tables)}")
print(f"Figures found: {len(figures)}")

print("\n=== Sample Recommendations ===")
for r in key_recommendations[:5]:
    print(f"Page {r['page']}: {r['content'][:100]}")

print("\n=== Tables ===")
for t in tables[:10]:
    print(f"Page {t['page']}: {t['id']} - {t['description'][:60]}")

print("\n=== Figures ===")
for f in figures[:10]:
    print(f"Page {f['page']}: {f['id']} - {f['description'][:60]}")

# 构建输出JSON
result = {
    "title": "中国抗癌协会乳腺癌诊治指南与规范（2026年版）",
    "source": "《中国癌症杂志》2025年第35卷第12期",
    "year": 2026,
    "language": "zh-CN",
    "total_pages": total_pages,
    "doi": "10.19401/j.cnki.1007-3639.2025.12.009",
    "document_type": "guideline_consensus",
    "issuing_body": "中国抗癌协会乳腺癌专业委员会，中华医学会肿瘤学分会乳腺肿瘤学组",
    "disease_area": "乳腺癌",
    "target_population": "乳腺癌患者及高危人群",
    "key_recommendations": [
        {
            "content": "一般风险人群乳腺癌筛查的起始年龄为40岁",
            "page": 1158
        },
        {
            "content": "乳腺癌高危人群筛查起始年龄可提前到40岁之前",
            "page": 1158
        },
        {
            "content": "乳腺X线检查对降低40岁以上女性乳腺癌死亡率作用明确",
            "page": 1158
        },
        {
            "content": "乳腺超声检查可推荐作为乳腺X线筛查的有效补充",
            "page": 1159
        },
        {
            "content": "BRCA1/2基因突变携带者可联合乳腺MRI进行筛查",
            "page": 1159
        },
        {
            "content": "高危人群每年1次乳腺X线检查，每6-12个月1次乳腺超声检查",
            "page": 1159
        },
        {
            "content": "他莫昔芬20mg/d连续服用5年可用于乳腺癌化学预防",
            "page": 1160
        },
        {
            "content": "预防性双乳切除术可降低90%以上的乳腺癌发病风险",
            "page": 1160
        },
        {
            "content": "预防性卵巢切除术可降低50%左右的乳腺癌发生风险",
            "page": 1160
        }
    ],
    "recommendation_strength": "基于循证医学证据的指南推荐",
    "_source_pdf": "guidelines\\2026\\中国抗癌协会乳腺癌诊治指南与规范（2026年版）.pdf",
    "key_pages": [
        {"description": "指南摘要与乳腺癌筛查", "page": 1158},
        {"description": "乳腺X线检查规范", "page": 1160},
        {"description": "乳腺超声检查规范", "page": 1164},
        {"description": "乳腺癌病理学诊断", "page": 1172},
        {"description": "浸润性乳腺癌保乳治疗", "page": 1177},
        {"description": "乳腺癌前哨淋巴结活检", "page": 1181},
        {"description": "乳腺癌全乳切除术后放疗", "page": 1183}
    ],
    "figures": figures[:20],
    "tables": tables[:20]
}

# 输出JSON
print("\n" + "="*60)
print("FINAL JSON OUTPUT:")
print("="*60)
print(json.dumps(result, ensure_ascii=False, indent=2))
