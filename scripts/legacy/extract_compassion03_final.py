import fitz
import json
import re

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\oncology\gastric_cancer\免疫一线\COMPASSION-03补充资料.pdf'
doc = fitz.open(pdf_path)

total_pages = len(doc)

# 读取所有页面内容
all_pages = []
for i in range(total_pages):
    page = doc[i]
    text = page.get_text()
    all_pages.append({'page': i+1, 'text': text})

# 收集表格信息
tables = []
page2_text = all_pages[1]['text']
# 改进的正则表达式以处理跨行标题
table_matches = re.findall(r'Table (S\d+)\.\s*((?:[^.\n]|\.(?!\.+))*?(?:\n(?![A-Za-z]*\s*Table)[^\n]*?)*?)\.{{3,}}\s*(\d+)', page2_text, re.MULTILINE)
for match in table_matches:
    table_num = match[0]
    table_title = match[1].strip().replace('\n', ' ')
    page_num = int(match[2])
    tables.append({
        "id": table_num,
        "title": table_title,
        "page": page_num
    })

# 收集图表信息
figures = []
figure_list_text = all_pages[1]['text']
fig_matches = re.findall(r'Figure (S\d+)~(S\d+)\.\s*([^\n]+)', figure_list_text)
for match in fig_matches:
    start_fig = match[0]
    end_fig = match[1]
    fig_title = match[2].strip()
    # 解析为单独图表
    if start_fig == 'S1' and end_fig == 'S3':
        # S1~S3是分开的图表
        figures.append({"id": "S1", "title": "Logistic regression analysis of safety response and cadonilimab exposure (part 1)", "page": 23})
        figures.append({"id": "S2", "title": "Logistic regression analysis of safety response and cadonilimab exposure (part 2)", "page": 23})
        figures.append({"id": "S3", "title": "Logistic regression analysis of safety response and cadonilimab exposure (part 3)", "page": 23})

# 添加S4和S5
figures.append({"id": "S4", "title": "RO (mean+SD) - time plots following multiple dose of cadonilimab", "page": 24})
figures.append({"id": "S5", "title": "CD4+Ki67+ T cell parent ratio to baseline (mean+SD) - time plots following multiple dose of cadonilimab", "page": 25})

# 构建关键发现
key_findings = []

# 从Table S3提取样本量信息
key_findings.append({
    "content": "Phase Ib total: N=69 patients (6 mg/kg Q2W: n=34; 10 mg/kg Q2W: n=3; 450 mg Q2W: n=32)",
    "page": 6
})
key_findings.append({
    "content": "Phase II total: N=145 patients (Cervical cancer: n=99; Esophageal carcinoma: n=22; Hepatocellular carcinoma: n=24)",
    "page": 6
})
key_findings.append({
    "content": "Total enrolled: N=214 patients across Phase Ib and Phase II",
    "page": 6
})

# 从Table S6提取随访信息
key_findings.append({
    "content": "Cervical cancer cohort: Median follow-up for PFS 13.1 months (95% CI: 11.0-15.6), for OS 14.6 months (95% CI: 13.7-16.0)",
    "page": 9
})
key_findings.append({
    "content": "Esophageal carcinoma cohort: Median follow-up for PFS 23.9 months, for OS 17.9 months",
    "page": 9
})
key_findings.append({
    "content": "Hepatocellular carcinoma cohort: Median follow-up for PFS 24.3 months, for OS 19.6 months",
    "page": 9
})

# 从Table S4提取入组时间
key_findings.append({
    "content": "Cervical cancer: First patient enrolled Sep. 26, 2019; Last patient enrolled Jan. 8, 2021",
    "page": 8
})
key_findings.append({
    "content": "Esophageal carcinoma: First patient enrolled Dec. 17, 2019; Last patient enrolled Dec. 2, 2020",
    "page": 8
})
key_findings.append({
    "content": "Hepatocellular carcinoma: First patient enrolled Oct. 31, 2019; Last patient enrolled Oct. 30, 2020",
    "page": 8
})

# ADA/免疫原性数据 (Table S3)
key_findings.append({
    "content": "Treatment-emergent ADA positive rate: Overall 7.0% (14/201 patients); Phase II cervical cancer 6.5% (6/92), HCC 23.8% (5/21)",
    "page": 6
})

# PK参数 (Table S1, S2)
key_findings.append({
    "content": "PK analysis showed dose-proportional exposure with median Cmax ranging from 128-174 μg/mL and AUC0-t from 287-433 day*μg/mL across dose levels",
    "page": 4
})

# 关键页面
key_pages = {
    "title_and_citation": 1,
    "table_of_contents": 2,
    "supplementary_methods": [2, 3],
    "pk_pd_methods": [2, 3],
    "supplementary_tables": list(range(4, 23)),
    "supplementary_figures": [23, 24, 25, 26],
    "definition": 26,
    "clinical_study_protocol": 27
}

# 构建最终输出
output = {
    "title": "Safety and antitumour activity of cadonilimab, an anti-PD-1/CTLA-4 bispecific antibody, for patients with advanced solid tumours (COMPASSION-03): a multicentre, open-label, phase 1b/2 trial - Supplementary Appendix",
    "source": "Lancet Oncology",
    "year": 2023,
    "language": "en",
    "total_pages": total_pages,
    "doi": "10.1016/S1470-2045(23)00346-3",
    "document_type": "original_research",
    "_source_pdf": "oncology\\gastric_cancer\\免疫一线\\COMPASSION-03补充资料.pdf",
    "trial_name": "COMPASSION-03 (AK104-201)",
    "study_design": "Multicentre, open-label, phase 1b/2 trial",
    "sample_size": {
        "phase_Ib": 69,
        "phase_II": 145,
        "total": 214,
        "breakdown": {
            "phase_Ib_6mg_kg": 34,
            "phase_Ib_10mg_kg": 3,
            "phase_Ib_450mg": 32,
            "phase_II_cervical_cancer": 99,
            "phase_II_esophageal_carcinoma": 22,
            "phase_II_hepatocellular_carcinoma": 24
        }
    },
    "primary_endpoint": None,
    "methodology": {
        "pk_analysis": "Non-compartmental methods using WinNonlin version 8.3. Endpoints included AUC0-t, Cmax, Tmax, Cmin, CL, t1/2, Vd, and accumulation ratio.",
        "pd_analysis": "CTLA-4 suppression via Ki67 marker and receptor occupancy (RO) on PD-1 and CTLA-4 of peripheral blood CD3+ T cells using flow cytometry.",
        "immunogenicity": "Electrochemiluminescent immunoassay using Meso Scale Discovery technology for ADA and NAb detection."
    },
    "key_findings": key_findings,
    "key_pages": key_pages,
    "figures": figures,
    "tables": tables
}

print(json.dumps(output, ensure_ascii=False, indent=2))
