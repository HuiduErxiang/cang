import fitz
import json

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\oncology\lung_cancer\NSCLC\KRAS\CodeBreaK 200研究.pdf'
doc = fitz.open(pdf_path)

# 读取所有页面内容
pages_content = []
for i in range(len(doc)):
    page = doc[i]
    pages_content.append(page.get_text())

doc.close()

# 构建JSON输出
result = {
    "title": "Sotorasib versus docetaxel for previously treated non-small-cell lung cancer with KRAS G12C mutation: a randomised, open-label, phase 3 trial (CodeBreaK 200)",
    "source": "The Lancet",
    "year": 2023,
    "language": "English",
    "total_pages": 14,
    "doi": "10.1016/S0140-6736(23)00221-0",
    "document_type": "original_research",
    "_source_pdf": r"oncology\lung_cancer\NSCLC\KRAS\CodeBreaK 200研究.pdf",
    "trial_name": "CodeBreaK 200",
    "study_design": "Randomised, open-label, phase 3 trial at 148 centres in 22 countries",
    "sample_size": "345 patients randomly assigned (171 sotorasib, 174 docetaxel)",
    "primary_endpoint": "Progression-free survival assessed by blinded independent central review",
    "methodology": "Patients aged ≥18 years with KRAS G12C-mutated advanced NSCLC who progressed after platinum-based chemotherapy and PD-1/PD-L1 inhibitor. Randomised 1:1 to oral sotorasib (960 mg once daily) or intravenous docetaxel (75 mg/m² every 3 weeks).",
    "key_findings": [
        {
            "content": "Median progression-free survival: 5.6 months (95% CI 4.3–7.8) with sotorasib vs 4.5 months (95% CI 3.0–5.7) with docetaxel; hazard ratio 0.66 (95% CI 0.51–0.86); p=0.0017",
            "page": 7
        },
        {
            "content": "Overall response rate: 28.1% (95% CI 21.5–35.4) with sotorasib vs 13.2% (95% CI 8.6–19.2) with docetaxel",
            "page": 8
        },
        {
            "content": "Disease control rate: 82.5% (95% CI 75.9–87.8) with sotorasib vs 60.3% (95% CI 52.7–67.7) with docetaxel",
            "page": 8
        },
        {
            "content": "Median overall survival: 10.6 months (95% CI 8.9–14.0) with sotorasib vs 11.3 months (95% CI 9.0–14.9) with docetaxel; HR 1.01 (95% CI 0.77–1.33); p=0.53 (not significant)",
            "page": 8
        },
        {
            "content": "Grade 3 or worse treatment-related adverse events: 33% (56/169) with sotorasib vs 40% (61/151) with docetaxel",
            "page": 9
        },
        {
            "content": "Serious treatment-related adverse events: 11% (18/169) with sotorasib vs 23% (34/151) with docetaxel",
            "page": 9
        },
        {
            "content": "Most common grade ≥3 adverse events with sotorasib: diarrhoea (12%), alanine aminotransferase increase (8%), aspartate aminotransferase increase (5%)",
            "page": 9
        },
        {
            "content": "Most common grade ≥3 adverse events with docetaxel: neutropenia (9%), fatigue (6%), febrile neutropenia (5%)",
            "page": 9
        },
        {
            "content": "Tumour shrinkage observed in 80% (127/158) of sotorasib-treated patients vs 63% (81/129) of docetaxel-treated patients",
            "page": 8
        }
    ],
    "key_pages": [1, 3, 5, 6, 7, 8, 9, 10],
    "figures": [
        {
            "number": "Figure 1",
            "title": "Trial profile",
            "page": 5
        },
        {
            "number": "Figure 2",
            "title": "Progression-free survival of sotorasib versus docetaxel (Kaplan-Meier curve and subgroup analyses)",
            "page": 7
        },
        {
            "number": "Figure 3",
            "title": "Overall response and overall survival (tumour burden change, best response, and OS Kaplan-Meier curve)",
            "page": 8
        },
        {
            "number": "Figure 4",
            "title": "Patient-reported outcomes of sotorasib versus docetaxel",
            "page": 10
        }
    ],
    "tables": [
        {
            "number": "Table 1",
            "title": "Baseline patient demographic and clinical characteristics",
            "page": 6
        },
        {
            "number": "Table 2",
            "title": "Adverse events",
            "page": 9
        },
        {
            "number": "Table 3",
            "title": "Treatment-related adverse events of any grade (occurring in ≥5% of patients) or of grade ≥3",
            "page": 9
        }
    ]
}

# 输出JSON
print(json.dumps(result, ensure_ascii=False, indent=2))
