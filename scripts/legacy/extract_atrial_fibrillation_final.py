import fitz
import json
import re

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\心血管\心房颤动诊断和治疗中国指南.pdf"
doc = fitz.open(pdf_path)

# 获取所有页面内容
all_text = ""
pages_content = []
for i in range(len(doc)):
    page = doc[i]
    text = page.get_text()
    pages_content.append({
        "page_num": i + 1,
        "text": text
    })
    all_text += text + "\n"

total_pages = len(doc)

# 构建JSON输出
title = "心房颤动诊断和治疗中国指南"

source = "中华医学会心血管病学分会,中国生物医学工程学会心律分会"

year = 2023

language = "zh"

doi = "10.3760/cma.j.cn112148-20230416-00221"

document_type = "guideline_consensus"

_source_pdf = "guidelines\\心血管\\心房颤动诊断和治疗中国指南.pdf"

issuing_body = "中华医学会心血管病学分会,中国生物医学工程学会心律分会"

disease_area = "心房颤动"

target_population = "心房颤动患者"

# 关键推荐意见
key_recommendations = [
    {
        "content": "建议使用CHA2DS2-VASc-60评分评估患者的血栓栓塞风险",
        "category": "卒中风险评估",
        "strength": "Ⅰ",
        "evidence": "B",
        "page": 4
    },
    {
        "content": "CHA2DS2-VASc-60评分≥2分的男性或≥3分的女性患者应使用口服抗凝药(OAC)",
        "category": "卒中预防",
        "strength": "Ⅰ",
        "evidence": "B",
        "page": 4
    },
    {
        "content": "CHA2DS2-VASc-60评分为1分的男性或2分的女性患者，在结合临床净获益和患者的意愿后应考虑使用OAC",
        "category": "卒中预防",
        "strength": "Ⅱa",
        "evidence": "B",
        "page": 4
    },
    {
        "content": "CHA2DS2-VASc-60评分为0分的男性或1分的女性患者不应以预防卒中为目的使用OAC",
        "category": "卒中预防",
        "strength": "Ⅲ",
        "evidence": "C",
        "page": 4
    },
    {
        "content": "OAC治疗应首选非维生素K拮抗剂口服抗凝药(NOAC)",
        "category": "抗凝治疗",
        "strength": "Ⅰ",
        "evidence": "A",
        "page": 7
    },
    {
        "content": "不应单独应用抗血小板治疗预防房颤相关卒中",
        "category": "抗凝治疗",
        "strength": "Ⅲ",
        "evidence": "A",
        "page": 7
    },
    {
        "content": "年龄≥65岁的人群在就医时，可考虑通过脉搏触诊或心电图进行房颤的机会性筛查",
        "category": "房颤筛查",
        "strength": "Ⅱa",
        "evidence": "A",
        "page": 4
    },
    {
        "content": "年龄≥70岁的人群，可考虑通过定期或连续心电监测进行房颤的系统性筛查",
        "category": "房颤筛查",
        "strength": "Ⅱa",
        "evidence": "A",
        "page": 4
    },
    {
        "content": "建议使用HAS-BLED评分系统评估出血风险，评分≥3分为高出血风险",
        "category": "出血风险评估",
        "strength": "Ⅱa",
        "evidence": "C",
        "page": 6
    },
    {
        "content": "在无抗凝绝对禁忌证的情况下，高出血风险不能作为启用OAC预防卒中的禁忌证",
        "category": "抗凝治疗",
        "strength": "Ⅲ",
        "evidence": "B",
        "page": 6
    },
    {
        "content": "对于诊断1年之内的房颤，节律控制策略在改善预后方面优于室率控制策略",
        "category": "节律控制",
        "strength": "Ⅰ",
        "evidence": "B",
        "page": 1
    },
    {
        "content": "导管消融逐渐成为房颤节律控制的一线治疗手段",
        "category": "节律控制",
        "strength": "Ⅰ",
        "evidence": "A",
        "page": 1
    }
]

# 推荐强度说明
recommendation_strength = {
    "Ⅰ": "证明和(或)公认某项诊断和治疗有益、有用、有效，推荐",
    "Ⅱa": "有关某项诊断和治疗的效用证据不一致或意见存在分歧，证据/意见的重量倾向于有用、有效，应该考虑",
    "Ⅱb": "证据/意见不足以充分支持有用、有效，可以考虑",
    "Ⅲ": "证明和(或)公认无效，在某些情况下可能有害，不推荐"
}

# 关键页面
key_pages = {
    "title_and_abstract": [1, 2],
    "epidemiology": [2],
    "clinical_assessment": [2, 3],
    "stroke_prevention": [4, 5, 6, 7, 8],
    "anticoagulation": [5, 6, 7, 8],
    "rhythm_control": [1],
    "catheter_ablation": [1],
    "references": [43, 44, 45, 46, 47]
}

# 表格信息
tables = [
    {
        "id": "表1",
        "title": "推荐类别",
        "description": "包括Ⅰ、Ⅱ、Ⅱa、Ⅱb、Ⅲ类推荐及其定义",
        "page": 2
    },
    {
        "id": "表2",
        "title": "证据级别",
        "description": "包括A、B、C三级证据及其定义",
        "page": 2
    },
    {
        "id": "表3",
        "title": "房颤的分类",
        "description": "包括阵发性房颤、持续性房颤、持久性房颤和永久性房颤的定义",
        "page": 3
    },
    {
        "id": "表4",
        "title": "房颤筛查",
        "description": "不同人群的房颤筛查建议",
        "page": 4
    },
    {
        "id": "表5",
        "title": "CHA2DS2-VASc-60评分",
        "description": "亚洲房颤患者卒中风险评估评分系统",
        "page": 4
    },
    {
        "id": "表6",
        "title": "房颤卒中风险评估及抗凝治疗",
        "description": "卒中风险评估及抗凝治疗推荐",
        "page": 5
    },
    {
        "id": "表7",
        "title": "HAS-BLED评分",
        "description": "出血风险评估评分系统",
        "page": 6
    },
    {
        "id": "表8",
        "title": "抗凝治疗出血危险因素",
        "description": "包括不可纠正、部分可纠正、可纠正危险因素及生物标志物",
        "page": 6
    },
    {
        "id": "表9",
        "title": "抗凝出血风险评估",
        "description": "抗凝出血风险评估的推荐建议",
        "page": 6
    },
    {
        "id": "表10",
        "title": "NOAC与华法林的有效性和安全性比较",
        "description": "各种NOAC与华法林的对比数据",
        "page": 7
    },
    {
        "id": "表11",
        "title": "NOAC剂量推荐",
        "description": "不同NOAC的标准剂量和低剂量推荐",
        "page": 7
    },
    {
        "id": "表12",
        "title": "NOAC药物代谢动力学及AAD对NOAC抗凝作用的影响",
        "description": "药物相互作用表格",
        "page": 7
    },
    {
        "id": "表13",
        "title": "房颤抗栓治疗药物",
        "description": "抗栓治疗药物的推荐",
        "page": 7
    },
    {
        "id": "表14",
        "title": "出血事件分类",
        "description": "轻度、中度、重度或致命性出血的定义",
        "page": 8
    },
    {
        "id": "表15",
        "title": "心房颤动抗凝合并出血的处理",
        "description": "出血处理推荐",
        "page": 8
    },
    {
        "id": "表16",
        "title": "心房颤动合并冠心病的抗栓治疗",
        "description": "合并冠心病时的抗栓策略",
        "page": 9
    },
    {
        "id": "表17",
        "title": "房颤合并CKD患者的抗凝治疗",
        "description": "慢性肾脏病患者抗凝治疗推荐",
        "page": 10
    }
]

# 图表信息
figures = [
    {
        "id": "图1",
        "title": "心房颤动合并冠心病的抗栓治疗",
        "description": "根据ACS/CCS和是否PCI制定抗栓策略流程图",
        "page": 9
    },
    {
        "id": "图2",
        "title": "根据肾功能调整的非维生素K拮抗剂口服抗凝药用法",
        "description": "不同肾功能水平下NOAC剂量调整方案",
        "page": 10
    }
]

# 构建最终JSON输出
output = {
    "title": title,
    "source": source,
    "year": year,
    "language": language,
    "total_pages": total_pages,
    "doi": doi,
    "document_type": document_type,
    "_source_pdf": _source_pdf,
    "issuing_body": issuing_body,
    "disease_area": disease_area,
    "target_population": target_population,
    "key_recommendations": key_recommendations,
    "recommendation_strength": recommendation_strength,
    "key_pages": key_pages,
    "figures": figures,
    "tables": tables
}

# 输出JSON
print(json.dumps(output, ensure_ascii=False, indent=2))
