import json

# 构建最终的JSON对象
guideline_data = {
    "title": "免疫检查点抑制剂相关的毒性管理指南",
    "source": "中国临床肿瘤学会（CSCO）",
    "year": 2023,
    "language": "中文",
    "total_pages": 204,
    "doi": None,
    "document_type": "guideline_consensus",
    "_source_pdf": "guidelines\\2023CSCO免疫检查点抑制剂相关的毒性管理指南.pdf",
    "issuing_body": "中国临床肿瘤学会（CSCO）指南工作委员会",
    "disease_area": "免疫检查点抑制剂（ICIs）相关毒性管理",
    "target_population": "接受免疫检查点抑制剂治疗的肿瘤患者，包括特殊人群（自身免疫性疾病患者、病毒性肝炎携带者、老年患者、器官移植患者等）",
    "key_recommendations": [
        {
            "content": "特殊人群筛查：自身免疫性疾病患者、HBV/HCV携带者、结核感染患者、老年患者可使用ICIs；妊娠期患者不推荐使用ICIs",
            "page": 24,
            "evidence_category": "2A类",
            "recommendation_grade": "Ⅰ级/Ⅱ级/Ⅲ级"
        },
        {
            "content": "毒性分级管理原则：G1继续使用ICIs不推荐糖皮质激素；G2暂停使用，口服泼尼松0.5-1mg/(kg·d)；G3住院治疗，静脉甲泼尼龙1-2mg/(kg·d)；G4考虑ICU，永久停用ICIs",
            "page": 38,
            "evidence_category": "2A类",
            "recommendation_grade": "Ⅰ级推荐"
        },
        {
            "content": "皮肤毒性管理：斑丘疹G1局部外用糖皮质激素，G2口服泼尼松0.5-1mg/(kg·d)，G3-4糖皮质激素抵抗可考虑英夫利西单抗、托珠单抗",
            "page": 43,
            "evidence_category": "2A类",
            "recommendation_grade": "Ⅰ级/Ⅱ级推荐"
        },
        {
            "content": "反应性皮肤毛细血管增生症（RCCEP）管理：G1继续治疗，局部保护；G2继续治疗，局部治疗；G3暂停治疗，待恢复至≤1级后恢复给药",
            "page": 51,
            "evidence_category": "2A类",
            "recommendation_grade": "Ⅰ级/Ⅱ级推荐"
        },
        {
            "content": "甲状腺功能减退管理：G1继续ICIs治疗，监测TSH及游离T4；G2继续ICIs治疗，TSH>10IU/ml时补充甲状腺素",
            "page": 54,
            "evidence_category": "2A类",
            "recommendation_grade": "Ⅰ级推荐"
        },
        {
            "content": "肝脏毒性管理：G1继续ICIs，监测肝功能；G2暂停ICIs，泼尼松0.5-1mg/(kg·d)；G3暂停ICIs，泼尼松1-2mg/(kg·d)，考虑联合免疫抑制治疗",
            "page": 56,
            "evidence_category": "2A类",
            "recommendation_grade": "Ⅰ级/Ⅱ级推荐"
        },
        {
            "content": "胃肠毒性（腹泻/结肠炎）管理：G1继续或暂停ICIs，对症处理；G2暂停ICIs，口服泼尼松1mg/(kg·d)；G3暂停，G4永久停用，静脉甲泼尼龙2mg/(kg·d)",
            "page": 60,
            "evidence_category": "2A类",
            "recommendation_grade": "Ⅰ级推荐"
        },
        {
            "content": "胰腺毒性管理：无症状性淀粉酶/脂肪酶升高需评估急性胰腺炎证据；急性胰腺炎G2暂停ICIs，泼尼松/甲泼尼龙0.5-1mg/(kg·d)，请消化内科会诊",
            "page": 66,
            "evidence_category": "2A类",
            "recommendation_grade": "Ⅰ级/Ⅱ级推荐"
        },
        {
            "content": "肺毒性（肺炎）管理：G1暂停ICIs，口服泼尼松1mg/(kg·d)；G2暂停ICIs，静脉甲泼尼龙1-2mg/(kg·d)；G3-4住院治疗，永久停用ICIs",
            "page": 72,
            "evidence_category": "2A类",
            "recommendation_grade": "Ⅰ级推荐"
        },
        {
            "content": "毒性监测：治疗前基线检查，治疗期间每2-3周复查血常规生化，每4-6周复查甲状腺功能、肺功能、心脏标志物等",
            "page": 165,
            "evidence_category": "2A类",
            "recommendation_grade": "Ⅰ级推荐"
        },
        {
            "content": "糖皮质激素使用注意事项：使用糖皮质激素（泼尼松>20mg/d持续≥4周）需预防卡氏肺孢子菌肺炎；使用>6周考虑抗真菌预防",
            "page": 40,
            "evidence_category": "2A类",
            "recommendation_grade": "注释建议"
        }
    ],
    "recommendation_strength": {
        "description": "CSCO诊疗指南采用三级推荐体系",
        "grade_1": "1A类证据和部分2A类证据，适应证明确、可及性好、纳入医保目录的措施",
        "grade_2": "1B类证据和部分2A类证据，国内外RCT提供高级别证据但可及性差或效价比不高",
        "grade_3": "2B类证据和3类证据，临床上习惯使用或有探索价值的措施",
        "evidence_categories": {
            "1A": "严谨的meta分析、大型随机对照研究，一致共识（支持意见≥80%）",
            "1B": "严谨的meta分析、大型随机对照研究，基本一致共识（支持意见60%-<80%）",
            "2A": "一般质量的meta分析、小型随机对照研究、设计良好的大型回顾性研究，一致共识",
            "2B": "一般质量的meta分析、小型随机对照研究，基本一致共识",
            "3": "非对照的单臂临床研究、病例报告、专家观点，无共识且争议大"
        }
    },
    "key_pages": {
        "title_page": 1,
        "preface": 9,
        "table_of_contents": [11, 12],
        "evidence_categories": 13,
        "recommendation_grades": 14,
        "update_highlights": [14, 20],
        "special_population_screening": [24, 36],
        "toxicity_management_principles": [38, 42],
        "skin_toxicity": [43, 53],
        "rccep": [51, 53],
        "endocrine_toxicity": [54, 59],
        "hepatic_toxicity": [56, 59],
        "gastrointestinal_toxicity": [60, 65],
        "pancreatic_toxicity": [66, 70],
        "pulmonary_toxicity": [72, 82],
        "musculoskeletal_toxicity": [83, 91],
        "infusion_reactions": [92, 95],
        "neurotoxicity": [96, 105],
        "hematologic_toxicity": [106, 119],
        "renal_toxicity": [120, 123],
        "cardiovascular_toxicity": [124, 135],
        "ocular_toxicity": [136, 141],
        "ototoxicity": [142, 145],
        "bladder_toxicity": [146, 150],
        "toxicity_monitoring": [165, 169],
        "appendix_restart_icis": 160,
        "appendix_toxicity_characteristics": [162, 164],
        "appendix_immunosuppressants": [170, 177],
        "appendix_early_recognition": [178, 184],
        "appendix_severe_refractory": [185, 194]
    },
    "figures": [],
    "tables": [
        {
            "number": "1",
            "title": "CSCO诊疗指南证据类别",
            "page": 13,
            "description": "证据类别分类表，包含1A、1B、2A、2B、3类证据的定义和共识度标准"
        },
        {
            "number": "2", 
            "title": "CSCO诊疗指南推荐等级",
            "page": 14,
            "description": "推荐等级标准表，包含Ⅰ级、Ⅱ级、Ⅲ级推荐的定义和标准"
        },
        {
            "number": "3",
            "title": "特殊人群筛查",
            "page": 24,
            "description": "特殊人群ICIs使用推荐，包括自身免疫性疾病、HBV/HCV携带者、结核感染、妊娠期等"
        },
        {
            "number": "4",
            "title": "基线检查",
            "page": [32, 34],
            "description": "ICIs治疗前基线检查项目，包括一般情况、影像学、血液学、皮肤黏膜、内分泌等检查"
        },
        {
            "number": "5",
            "title": "毒性分级管理原则",
            "page": 38,
            "description": "ICIs相关毒性分级（G1-G4）的管理原则，包括住院级别、糖皮质激素使用、免疫抑制剂使用和ICIs治疗决策"
        },
        {
            "number": "6",
            "title": "皮肤毒性管理",
            "page": [43, 46],
            "description": "斑丘疹/皮疹、瘙痒、大疱性皮炎的分级管理推荐"
        },
        {
            "number": "7",
            "title": "反应性皮肤毛细血管增生症（RCCEP）",
            "page": 51,
            "description": "RCCEP G1-G3分级管理推荐"
        },
        {
            "number": "8",
            "title": "内分泌毒性",
            "page": [54, 58],
            "description": "甲状腺功能减退、甲状腺功能亢进、垂体炎、肾上腺功能不全的分级管理"
        },
        {
            "number": "9",
            "title": "肝脏毒性",
            "page": 56,
            "description": "免疫相关性肝毒性G1-G4分级管理推荐"
        },
        {
            "number": "10",
            "title": "胃肠毒性（腹泻/结肠炎）",
            "page": [60, 62],
            "description": "腹泻/结肠炎G1-G4分级管理推荐"
        },
        {
            "number": "11",
            "title": "胰腺毒性",
            "page": [66, 69],
            "description": "无症状性淀粉酶/脂肪酶升高和急性胰腺炎的分级管理"
        },
        {
            "number": "12",
            "title": "毒性监测",
            "page": [165, 168],
            "description": "ICIs治疗期间的监测项目和推荐等级"
        },
        {
            "number": "13",
            "title": "常用免疫抑制剂的用法、初始剂量和适应证",
            "page": [170, 174],
            "description": "全身/局部皮质类固醇、抗TNF-α药物、IL-6抑制剂等药物的用法和剂量"
        }
    ]
}

# 输出JSON
print(json.dumps(guideline_data, ensure_ascii=False, indent=2))
