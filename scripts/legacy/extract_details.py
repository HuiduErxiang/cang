import fitz
import re

pdf_path = r".\raw\pdf\guidelines\专家共识\德曲妥珠单抗临床管理路径及不良反应处理中国专家共识（2024版）.pdf"
doc = fitz.open(pdf_path)

# 查找推荐意见
recommendations = []
for i in range(len(doc)):
    page = doc[i]
    text = page.get_text()
    # 查找推荐意见
    matches = re.findall(r'推荐意见\d+[：:]([^。]+)[。\n]', text)
    for m in matches:
        recommendations.append({"content": m.strip(), "page": i+1})

print("=== 推荐意见 ===")
for r in recommendations:
    print(f"第{r['page']}页: 推荐意见: {r['content'][:100]}...")

# 查找表格详细信息
tables = []
table_info = [
    ("表1", r'表1.*?T-DXd在晚期乳腺癌治疗领域已公布结果的临床试验汇总', 3),
    ("表2", r'表2.*?T-DXd在乳腺癌领域正在进行的临床试验汇总', 4),
    ("表3", r'表3.*?不同研究中T-DXd治疗乳腺癌的常见不良事件发生率', 5),
    ("表4", r'表4.*?发生LVEF下降不良事件时T-DXd的剂量调整', 11),
]

for tid, pattern, page in table_info:
    text = doc[page-1].get_text()
    match = re.search(pattern, text)
    if match:
        title = match.group(0).strip()
        tables.append({"id": tid, "title": title, "page": page})
        print(f"{tid}: {title} (第{page}页)")

# 查找图详细信息
print("\n=== 图 ===")
figures = []
figure_info = [
    ("图1", r'图1.*?T-DXd中性粒细胞减少不良事件的二级预防路径', 7),
    ("图2", r'图2.*?T-DXd治疗相关ILD/肺炎的临床管理流程', 10),
    ("图3", r'图3.*?T-DXd临床管理路径', 13),
]

for fid, pattern, page in figure_info:
    text = doc[page-1].get_text()
    match = re.search(pattern, text)
    if match:
        title = match.group(0).strip()
        figures.append({"id": fid, "title": title, "page": page})
        print(f"{fid}: {title} (第{page}页)")

# 查找通信作者
print("\n=== 通信作者 ===")
for i in range(len(doc)):
    text = doc[i].get_text()
    if '通信作者' in text:
        lines = text.split('\n')
        for line in lines:
            if '通信作者' in line:
                print(f"第{i+1}页: {line[:300]}")

doc.close()
