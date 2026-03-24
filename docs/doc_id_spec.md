# doc_id 生成规则

**版本**: 1.0  
**冻结日期**: 2026-03-23  
**适用范围**: 藏经阁所有文献的唯一标识

---

## 一、格式定义

```
{category}_{short_name}_{hash8}
```

| 字段 | 说明 | 示例 |
|---|---|---|
| `category` | 文献所属大类，取自 source_index 分组 | `oncology`, `neurology`, `guidelines`, `conferences`, `epidemiology` |
| `short_name` | 文献的简短英文标识，全小写，用下划线分隔 | `clarity_ad`, `keynote811`, `csco_gastric_2024` |
| `hash8` | 源 PDF 文件内容的 SHA-256 前 8 位（小写 hex） | `a539f72e` |

### 完整示例

```
oncology_keynote811_0015101e
neurology_clarity_ad_a539f72e
guidelines_csco_gastric_2024_5cecf07b
conferences_asco_gi_hcc_2025_a02dd8d0
```

---

## 二、生成规则

### 2.1 hash8 的计算

```python
import hashlib

def compute_hash8(pdf_path: str) -> str:
    """计算 PDF 文件 SHA-256 前 8 位"""
    sha256 = hashlib.sha256()
    with open(pdf_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()[:8]
```

### 2.2 short_name 的生成

1. 优先使用研究名称（如 `clarity_ad`、`keynote811`、`rainbow_asia`）
2. 无研究名称的指南/共识，使用 `{组织}_{疾病}_{年份}`（如 `csco_gastric_2024`）
3. 中文标题先翻译为对应英文缩写（如 `csco_cervical_2023`）
4. 全部小写，空格和连字符替换为下划线

### 2.3 category 的取值

固定枚举值如下：

| category | 适用于 |
|---|---|
| `oncology` | 肿瘤学临床研究 |
| `neurology` | 神经科学研究 |
| `guidelines` | 指南/共识/规范 |
| `conferences` | 会议摘要/海报/口头报告 |
| `epidemiology` | 流行病学/公共卫生 |
| `methodology` | 方法学/检测/标志物 |
| `supportive_care` | 支持治疗/不良反应管理 |

如有新类别，先在本文档新增枚举值，再使用。

---

## 三、稳定性约束

1. **doc_id 一旦生成，不得变更**。即使后续文件重命名、重新分类，doc_id 不变。
2. **hash8 基于原始 PDF 内容**，与文件名无关。相同 PDF 无论叫什么名、放在哪，生成的 hash8 相同。
3. **禁止使用文件名作为 doc_id**。文件名会变，doc_id 不会。

---

## 四、边界情况

### 同一研究的主文和补充材料

**各自独立 doc_id**。

理由：主文和补充材料是不同的 PDF 文件（不同 hash），蒸馏结果也不同。但通过 `short_name` 前缀保持可关联性。

示例：
```
oncology_clarity_ad_a539f72e          ← 主文
oncology_clarity_ad_supp_093cca54     ← 补充附录
oncology_clarity_ad_safety_0adf91f6   ← 安全性报告
```

### 同一 PDF 的不同蒸馏版本

doc_id 不变。蒸馏版本由 `distillation_version` 字段区分，doc_id 绑定的是文献身份，不是蒸馏结果。

### 重复入仓的同一 PDF

因为 hash8 相同，所以 doc_id 相同，自动去重。如果 category 或 short_name 不同导致 doc_id 不同，以**首次入仓时的 doc_id 为准**。

---

## 五、与现有蒸馏文件的对应

当前 `output/distillation_samples/` 中的文件已经使用了 `{title}_{hash8}.json` 的命名。迁移策略：

1. 保留现有文件名不变（它们只是文件名，不是 doc_id）
2. 在蒸馏 JSON 的顶层新增 `doc_id` 字段
3. 在 `lineage/` 中建立 `doc_id → source_pdf → distillation_file` 的映射

---

## 六、注册与查询

所有 doc_id 注册到 `lineage/doc_registry.json`，结构如下：

```json
{
  "oncology_keynote811_0015101e": {
    "doc_id": "oncology_keynote811_0015101e",
    "category": "oncology",
    "short_name": "keynote811",
    "hash8": "0015101e",
    "source_pdf": "raw/pdf/oncology/KEYNOTE-811.pdf",
    "title": "KEYNOTE-811: Pembrolizumab plus chemotherapy in gastric cancer",
    "created_at": "2026-03-23",
    "distillation_versions": ["v1.0"]
  }
}
```
