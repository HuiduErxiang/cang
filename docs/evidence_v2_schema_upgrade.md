# evidence_v2 Schema 升级规约

**版本**: 1.0  
**冻结日期**: 2026-03-23  
**目标**: 让 evidence_v2.json 中的 fact 和 source 携带研究边界标签

---

## 一、当前结构（Before）

### v2_facts 当前字段

```json
{
  "fact_id": "V2-FACT-LECANEMAB-EFFICACY-001",
  "fact_key": "FACT-LECANEMAB-CDRSB-CFB-18MO",
  "domain": "efficacy",
  "definition": "Change from baseline in CDR-SB at 18 months",
  "definition_zh": "18个月时CDR-SB较基线变化",
  "value": "-0.45",
  "unit": "points",
  "fragment_ids": ["V2-FRAG-LECANEMAB-CLARITY-AD-001"],
  "status": "active",
  "lineage": {
    "source_key": "SRC-LECANEMAB-CLARITY-AD-2023-NEJM",
    "asset_key": "AST-LECANEMAB-CLARITY-AD-PRIMARY",
    "extraction_date": "2026-03-22"
  },
  "v1_mapping": { ... }
}
```

### v2_sources 当前字段

```json
{
  "source_id": "V2-SRC-LECANEMAB-CLARITY-AD-001",
  "source_type": "journal_article",
  "source_key": "SRC-LECANEMAB-CLARITY-AD-2023-NEJM",
  "title": "Lecanemab in Early Alzheimer's Disease",
  "citation": "van Dyck CH, et al. N Engl J Med. 2023",
  "v1_source_id": "SRC_CLARITY_AD_2024Q2_ORIGINAL",
  "metadata": {
    "journal": "N Engl J Med",
    "year": 2023,
    "doi": "10.1056/NEJMoa2212948",
    "study_type": "pivotal_phase3_RCT",
    "indication": "early_alzheimers_disease",
    "sample_size": 1795
  }
}
```

---

## 二、升级结构（After）

### v2_facts 新增字段

在每个 fact 对象中新增 `boundary_tags` 嵌套对象：

```json
{
  "fact_id": "V2-FACT-LECANEMAB-EFFICACY-001",
  "fact_key": "FACT-LECANEMAB-CDRSB-CFB-18MO",
  "domain": "efficacy",
  "definition": "Change from baseline in CDR-SB at 18 months",
  "definition_zh": "18个月时CDR-SB较基线变化",
  "value": "-0.45",
  "unit": "points",
  "fragment_ids": ["V2-FRAG-LECANEMAB-CLARITY-AD-001"],
  "status": "active",
  "lineage": { ... },
  "v1_mapping": { ... },
  "boundary_tags": {
    "claim_ceiling": "clinical_outcome",
    "study_subject": "human",
    "endpoint_nature": "clinical_scale"
  }
}
```

**fact 级别携带 3 个字段**：
- `claim_ceiling`：该事实的表述上限
- `study_subject`：该事实涉及的研究对象
- `endpoint_nature`：该事实的终点性质

### v2_sources 新增字段

在每个 source 的 `metadata` 中新增边界标签字段：

```json
{
  "source_id": "V2-SRC-LECANEMAB-CLARITY-AD-001",
  "source_type": "journal_article",
  "source_key": "SRC-LECANEMAB-CLARITY-AD-2023-NEJM",
  "title": "Lecanemab in Early Alzheimer's Disease",
  "citation": "...",
  "v1_source_id": "...",
  "metadata": {
    "journal": "N Engl J Med",
    "year": 2023,
    "doi": "10.1056/NEJMoa2212948",
    "study_type": "pivotal_phase3_RCT",
    "indication": "early_alzheimers_disease",
    "sample_size": 1795,
    "boundary_tags": {
      "document_type": "clinical_trial",
      "evidence_purpose": "efficacy",
      "claim_ceiling": "clinical_outcome",
      "study_subject": "human",
      "population_or_model": "MCI due to AD and mild AD dementia",
      "endpoint_nature": "clinical_scale",
      "boundary_tags_version": "1.0",
      "tagging_confidence": 0.95,
      "tagged_by": "llm_auto",
      "tagged_at": "2026-03-23T00:00:00Z"
    }
  }
}
```

**source 级别携带完整 6 个字段 + 元数据**：
- `document_type`：文献类型
- `evidence_purpose`：证据用途
- `claim_ceiling`：表述上限（source 级别的默认值）
- `study_subject`：研究对象
- `population_or_model`：人群或模型
- `endpoint_nature`：终点性质

---

## 三、设计决策说明

### 为什么 fact 和 source 都要带标签？

- **source 标签** = 文献级别的默认边界（如"这是一篇动物研究"）
- **fact 标签** = 事实级别的精确边界（如"该事实来自动物模型的机制发现"）

大多数情况下 fact 继承 source 的标签。但以下场景需要独立标签：

1. 混合型文献（同一篇论文有多种终点）
2. 同一篇临床研究同时包含 efficacy fact 和 biomarker fact

### 标签字段的冗余与透传

- `claim_ceiling` 同时出现在 source 和 fact 中。**如果 fact 没有独立标签，从 source 继承**。
- 侠客岛消费时，**优先读取 fact 级别标签**，缺失则 fallback 到 source 级别。

---

## 四、rebuild_manifest 新增字段

在 evidence_v2.json 的顶层 `rebuild_manifest` 中新增：

```json
{
  "rebuild_manifest": {
    "manifest_version": "1.1",
    "rebuild_date": "2026-03-23",
    "boundary_tags_schema_version": "1.0",
    "boundary_tags_coverage": {
      "total_sources": 5,
      "tagged_sources": 5,
      "total_facts": 18,
      "tagged_facts": 18
    }
  }
}
```

---

## 五、向后兼容

- 旧版 evidence_v2.json 中没有 `boundary_tags` 字段，侠客岛读取时应做 null check
- 如果 `boundary_tags` 缺失，侠客岛应按 `claim_ceiling = "clinical_outcome"` 作为默认值（最宽松，不额外约束）
- 这保证了升级过程中旧数据不会 break
