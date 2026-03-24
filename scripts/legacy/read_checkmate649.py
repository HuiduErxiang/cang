import fitz
import json

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\oncology\gastric_cancer\免疫一线\checkmate649 中国亚组.pdf'
doc = fitz.open(pdf_path)

# 收集所有页面的文本
all_pages = []
for i in range(len(doc)):
    page = doc[i]
    text = page.get_text()
    all_pages.append({'page': i+1, 'text': text})

# 获取完整文本
full_text = all_pages[0]['text']

# 构建JSON输出
output = {
    "title": "First-line nivolumab (NIVO) plus chemotherapy (chemo) vs chemo in patients with advanced gastric cancer/gastroesophageal junction cancer/esophageal adenocarcinoma (GC/GEJC/EAC): CheckMate 649 Chinese subgroup analysis 2-year follow-up",
    "source": "Annals of Oncology",
    "year": 2022,
    "language": "en",
    "total_pages": 1,
    "doi": "10.1016/j.annonc.2022.04.176",
    "document_type": "original_research",
    "_source_pdf": "oncology\\gastric_cancer\\免疫一线\\checkmate649 中国亚组.pdf",
    "trial_name": "CheckMate 649",
    "study_design": "Phase 3 randomized controlled trial (Chinese subgroup analysis)",
    "sample_size": {
        "total": 208,
        "nivo_plus_chemo": 99,
        "chemo": 106,
        "pd_l1_cps_ge_5": 156
    },
    "primary_endpoint": "Overall survival (OS) and progression-free survival (PFS) by blinded independent central review in patients with PD-L1 combined positive score (CPS) ≥ 5",
    "methodology": "Adults with previously untreated, unresectable advanced or metastatic GC/GEJC/EAC were enrolled regardless of PD-L1 expression. Patients with known HER2-positive status were excluded. Patients were randomized to receive NIVO (360 mg Q3W or 240 mg Q2W) + chemo (XELOX Q3W or FOLFOX Q2W), NIVO + ipilimumab, or chemo. Minimum follow-up was 25 months.",
    "key_findings": [
        {
            "content": "In patients with PD-L1 CPS ≥ 5, median OS was 15.5 months (95% CI: 11.9-21.1) for NIVO + chemo vs 9.6 months (95% CI: 8.0-12.1) for chemo (HR 0.56, 95% CI 0.38-0.81)",
            "page": 1
        },
        {
            "content": "In all randomized patients, median OS was 14.3 months (95% CI: 11.5-16.5) for NIVO + chemo vs 10.3 months (95% CI: 8.1-12.1) for chemo (HR 0.63, 95% CI 0.46-0.86)",
            "page": 1
        },
        {
            "content": "In patients with PD-L1 CPS ≥ 5, median PFS was 8.5 months (95% CI: 6.0-14.0) for NIVO + chemo vs 4.3 months (95% CI: 4.1-6.5) for chemo (HR 0.51, 95% CI 0.34-0.76)",
            "page": 1
        },
        {
            "content": "In all randomized patients, median PFS was 8.3 months (95% CI: 6.2-12.4) for NIVO + chemo vs 5.6 months (95% CI: 4.2-6.8) for chemo (HR 0.57, 95% CI 0.41-0.80)",
            "page": 1
        },
        {
            "content": "Objective response rate (ORR) in patients with PD-L1 CPS ≥ 5 was 68% vs 48% and median duration of response (DOR) was 12.5 months vs 6.9 months for NIVO + chemo vs chemo",
            "page": 1
        },
        {
            "content": "ORR in all randomized patients was 66% vs 45% and median DOR was 12.5 months vs 5.6 months for NIVO + chemo vs chemo",
            "page": 1
        },
        {
            "content": "Grade 3/4 treatment-related adverse events (TRAEs) occurred in 66% and 50% of patients with NIVO + chemo vs chemo",
            "page": 1
        },
        {
            "content": "Any-grade TRAEs leading to discontinuation were observed in 49% and 26% of patients for NIVO + chemo vs chemo",
            "page": 1
        },
        {
            "content": "Patient population: 88% had gastric cancer, 12% had GEJC, no patients had EAC; 75% had PD-L1 CPS ≥ 5",
            "page": 1
        }
    ],
    "key_pages": {
        "abstract": 1,
        "background": 1,
        "methods": 1,
        "results": 1,
        "conclusions": 1
    },
    "figures": [],
    "tables": []
}

# 写入文件
with open('output_checkmate649.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(json.dumps(output, ensure_ascii=False, indent=2))
