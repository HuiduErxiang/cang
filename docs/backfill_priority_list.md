# 回填优先级清单

**版本**: 1.0  
**冻结日期**: 2026-03-23  
**总工作量**: 共计 201 篇蒸馏文献样本，需用 LLM 进行边界标签打标并重建 evidence_v2。

---

## 优先级梯队定义

根据当前侠客岛生产线的消费需求和紧迫程度，将存量文献的 `boundary_tags` 回填分为三批：

### 第一批：极高优（阿尔茨海默病产品线）
- **包含对象**: lecanemab, donanemab 相关文献
- **涉及文档数**: 约 7 篇蒸馏样本
- **预期消费方**: `consumers/xiakedao` 下的阿尔茨海默病内容生成管线
- **要求时效**: 立即执行（本阶段核心目标）

### 第二批：高优（胃癌产品线）
- **包含对象**: 胃癌靶向/免疫相关文献 (含 Keynote-811, Keynote-062, Rainbow, Spotlight, Orient, ToGA, AVAGAST, HER2, CheckMate649, Rationale 等)
- **涉及文档数**: 约 36 篇蒸馏样本
- **预期消费方**: `consumers/xiakedao` 下的胃癌内容生成管线
- **要求时效**: 紧接第一批执行（本阶段核心目标）
- **注**: `胃癌抗HER2治疗中国专家共识(2024年版)` 已作为端到端验证完成回填。

### 第三批：常规（其余产品线）
- **包含对象**: 其他疾病领域的文献指南、前列腺癌、各大会议摘要等
- **涉及文档数**: 约 158 篇蒸馏样本
- **要求时效**: 本轮整改暂不执行，作为日常维护逐步回填。

---

## 第一、二批优先回填目标文件清单

（基于当前 `output/distillation_samples/` 的粗筛匹配结果）

**AD/神经 (第一批) 示例目标**:
- `clarity_ad_270e7367.json`
- `TRAILBLAZER-ALZ 2_5a505256.json`
- `TRAILBLAZER-ALZ 6_1ccabab2.json`
- `目前的证据基础是否支持仑卡奈单抗继续给药...json`
- 等共计 7 篇

**胃癌/消化道 (第二批) 示例目标**:
- `KEYNOTE-811_0015101e.json`
- `KEYNOTE-062原文_d4a1325e.json`
- `Rainbow原文_74621032.json`
- `SPOTLIGHT研究_d5a34024.json`
- `ORIENT-16原文_3a9304ec.json`
- `AVAGAST研究贝伐珠单抗化疗一线_4a252ba5.json`
- `ToGA研究_cfe4f5a5.json`
- `checkmate 649...`
- 等共计约 36 篇

---

## 执行建议

1. 开发一个批处理脚本，针对上述第一、二批共 ~43 篇 JSON 文件调用 LLM 抽取 boundary tags。
2. 提取出 tags 后覆盖更新原 json 文件（注入 `boundary_tags` 字典及 `doc_id` 等缺失字段）。
3. 针对 confidence < 0.8 的条目汇总人工复核。
4. 提供脚本重建对应的 `evidence_v2.json`，并覆盖至 `staging/evidence/rebuilt/` 目录。
