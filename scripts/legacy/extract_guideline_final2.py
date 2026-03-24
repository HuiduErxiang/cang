import fitz
import json
import re

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2026\中国抗癌协会乳腺癌诊治指南与规范（2026年版）.pdf'
doc = fitz.open(pdf_path)

total_pages = len(doc)

figures = []
tables = []

# 扫描所有页面提取表格和图信息
for page_idx in range(total_pages):
    page = doc[page_idx]
    text = page.get_text()
    page_num = page_idx + 1
    
    # 查找附录
    appendix_matches = re.findall(r'(附录[IVX\d]+[:：][^\n]{0,100})', text)
    for m in appendix_matches:
        tables.append({
            'id': m.split('：')[0].strip() if '：' in m else m[:10].strip(),
            'description': m.strip()[:150],
            'page': page_num
        })
    
    # 查找表格
    table_matches = re.findall(r'(表\s*\d+[\-\.]?\d*\s*[:：][^\n]{0,150})', text)
    for m in table_matches:
        match = re.search(r'表\s*\d+[\-\.]?\d*', m)
        if match:
            tables.append({
                'id': match.group().replace(' ', ''),
                'description': m.strip()[:200],
                'page': page_num
            })
    
    # 查找图
    fig_matches = re.findall(r'(图\s*\d+[\-\.]?\d*\s*[:：][^\n]{0,150})', text)
    for m in fig_matches:
        match = re.search(r'图\s*\d+[\-\.]?\d*', m)
        if match:
            figures.append({
                'id': match.group().replace(' ', ''),
                'description': m.strip()[:200],
                'page': page_num
            })

doc.close()

# 去重并保持顺序
def dedup(items):
    seen = set()
    result = []
    for item in items:
        key = (item['id'], item['page'])
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

tables = dedup(tables)
figures = dedup(figures)

# 构建最终JSON
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
        {"content": "一般风险人群乳腺癌筛查的起始年龄为40岁", "page": 1158},
        {"content": "乳腺癌高危人群筛查起始年龄可提前到40岁之前", "page": 1158},
        {"content": "乳腺X线检查对降低40岁以上女性乳腺癌死亡率作用明确", "page": 1158},
        {"content": "乳腺超声检查可推荐作为乳腺X线筛查的有效补充，尤其针对致密型乳腺", "page": 1159},
        {"content": "BRCA1/2基因突变携带者可联合乳腺MRI进行筛查", "page": 1159},
        {"content": "高危人群每年1次乳腺X线检查，每6-12个月1次乳腺超声检查，必要时联合乳腺增强MRI", "page": 1159},
        {"content": "他莫昔芬20mg/d连续服用5年可用于乳腺癌化学预防，适用于Gail模型评估5年风险≥1.67%者", "page": 1160},
        {"content": "雷洛昔芬60mg/d连续服用5年适用于绝经后女性乳腺癌预防", "page": 1160},
        {"content": "芳香化酶抑制剂（依西美坦25mg/d或阿那曲唑1mg/d）连续服用5年适用于绝经后女性", "page": 1160},
        {"content": "预防性双乳切除术可降低90%以上的乳腺癌发病风险，适用于BRCA1/2突变携带者", "page": 1160},
        {"content": "预防性卵巢切除术可降低50%左右的乳腺癌发生风险和80%以上的卵巢癌发生风险", "page": 1160},
        {"content": "参照美国放射学会BI-RADS分类标准进行乳腺影像报告", "page": 1161},
        {"content": "BI-RADS 3类恶性可能性为0%-2%，建议短期随访（6个月）", "page": 1163},
        {"content": "BI-RADS 4类恶性可能性为2%-95%，需要介入性诊断", "page": 1163},
        {"content": "BI-RADS 5类高度怀疑恶性（≥95%），临床应采取适当措施", "page": 1164},
        {"content": "浸润性乳腺癌保乳治疗需满足原发肿瘤最大径≤3cm等条件", "page": 1177},
        {"content": "前哨淋巴结活检适用于临床腋窝淋巴结阴性的早期乳腺癌患者", "page": 1181},
        {"content": "乳腺癌全乳切除术后放疗适应症包括淋巴结阳性、肿瘤>5cm等", "page": 1183}
    ],
    "recommendation_strength": "基于循证医学证据的指南推荐",
    "_source_pdf": "guidelines\\2026\\中国抗癌协会乳腺癌诊治指南与规范（2026年版）.pdf",
    "key_pages": [
        {"description": "指南摘要与乳腺癌筛查定义、目的及分类", "page": 1158},
        {"description": "乳腺癌筛查措施（X线、超声、MRI）", "page": 1158},
        {"description": "一般风险女性乳腺癌筛查指南", "page": 1159},
        {"description": "乳腺癌高危人群筛查意见", "page": 1159},
        {"description": "乳腺癌预防措施（一级预防、化学预防、预防性手术）", "page": 1160},
        {"description": "常规乳腺X线检查技术规范", "page": 1160},
        {"description": "乳腺X线诊断报告BI-RADS分类标准", "page": 1161},
        {"description": "乳腺超声检查仪器与方法", "page": 1164},
        {"description": "乳腺MRI检查规范", "page": 1168},
        {"description": "影像学引导下的乳腺活体组织病理学检查", "page": 1170},
        {"description": "乳腺癌病理学诊断报告规范", "page": 1172},
        {"description": "浸润性乳腺癌保乳治疗临床指南", "page": 1177},
        {"description": "乳腺癌前哨淋巴结活检临床指南", "page": 1181},
        {"description": "乳腺癌全乳切除术后放疗临床指南", "page": 1183}
    ],
    "figures": figures[:25],
    "tables": tables[:25]
}

# 输出JSON
print(json.dumps(result, ensure_ascii=False, indent=2))
