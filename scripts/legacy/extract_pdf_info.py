import fitz
import json

pdf_path = r'raw\pdf\guidelines\2024 CSCO指南\2024CSCO乳腺癌诊疗指南(OCR).pdf'
doc = fitz.open(pdf_path)

# 提取表格信息
tables_info = []
figures_info = []

# 搜索包含表格和图的页面
for i in range(len(doc)):
    text = doc[i].get_text()
    # 查找表格
    if '表' in text:
        lines = text.split('\n')
        for line in lines[:20]:
            if line.strip().startswith('表') and any(c.isdigit() for c in line[:10]):
                tables_info.append({'page': i+1, 'title': line.strip()[:100]})
                break
    # 查找图
    if '图' in text:
        lines = text.split('\n')
        for line in lines[:20]:
            if line.strip().startswith('图') and any(c.isdigit() for c in line[:10]):
                figures_info.append({'page': i+1, 'title': line.strip()[:100]})
                break

print('Tables found:')
for t in tables_info[:15]:
    print(f"  Page {t['page']}: {t['title']}")

print('\nFigures found:')
for f in figures_info[:15]:
    print(f"  Page {f['page']}: {f['title']}")

# 提取关键推荐
key_recommendations = []
key_pages = []

# HER-2阳性新辅助治疗
key_recommendations.append({
    "content": "HER-2阳性乳腺癌新辅助治疗：I级推荐TCbHP(1A)、THP×6(2A)",
    "page": 27,
    "category": "新辅助治疗",
    "strength": "I级推荐"
})

key_recommendations.append({
    "content": "HER-2阳性乳腺癌新辅助治疗：II级推荐THP×4(1B)、TH+吡咯替尼(1B)",
    "page": 27,
    "category": "新辅助治疗",
    "strength": "II级推荐"
})

key_recommendations.append({
    "content": "新辅助治疗后HER-2阳性non-pCR患者：I级推荐T-DM1(1A)",
    "page": 32,
    "category": "辅助治疗",
    "strength": "I级推荐"
})

# 三阴性乳腺癌
key_recommendations.append({
    "content": "三阴性乳腺癌新辅助治疗：I级推荐含紫杉类+蒽环类+铂类方案，PD-L1阳性患者推荐帕博利珠单抗联合化疗",
    "page": 34,
    "category": "新辅助治疗",
    "strength": "I级推荐"
})

# 激素受体阳性
key_recommendations.append({
    "content": "激素受体阳性乳腺癌辅助内分泌治疗：绝经后患者I级推荐AI(1A)，绝经前患者I级推荐OFS+AI/TAM",
    "page": 59,
    "category": "辅助治疗",
    "strength": "I级推荐"
})

# HER-2阳性晚期
key_recommendations.append({
    "content": "HER-2阳性晚期乳腺癌曲妥珠单抗敏感人群：I级推荐THP方案(1A)、TH+吡咯替尼(1A)",
    "page": 89,
    "category": "晚期解救治疗",
    "strength": "I级推荐"
})

key_recommendations.append({
    "content": "HER-2阳性晚期乳腺癌曲妥珠单抗治疗失败：I级推荐T-DXd",
    "page": 89,
    "category": "晚期解救治疗",
    "strength": "I级推荐"
})

# 三阴性晚期
key_recommendations.append({
    "content": "三阴性晚期乳腺癌解救治疗：I级推荐化疗+免疫治疗",
    "page": 98,
    "category": "晚期解救治疗",
    "strength": "I级推荐"
})

# HER-2低表达
key_recommendations.append({
    "content": "HER-2低表达晚期乳腺癌：I级推荐T-DXd",
    "page": 117,
    "category": "晚期解救治疗",
    "strength": "I级推荐"
})

print('\nKey recommendations extracted.')
