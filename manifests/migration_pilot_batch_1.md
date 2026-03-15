# 首批知识迁移映射清单

> **日期**: 2026-03-15
> **批次**: Pilot Batch 1
> **状态**: 已完成

## 1. 迁移概览

| 原路径 | 目标层 | 目标路径 | 文件数 | 迁移原因 |
|--------|--------|----------|--------|----------|
| V2 rules/l1_writing_craft/ | L1 | 藏经阁/l1/writing_craft/ | 8 | 写作心法层，属于正式知识 |
| V2 intake/manifests/ | staging | 藏经阁/staging/intake_manifests/ | 2 | 摄取清单，属于中间产物 |

## 2. 详细映射

### 2.1 L1 写作心法层

**原路径**: `D:\汇度编辑部1\写作知识库\medical_kb_system_v2\rules\l1_writing_craft\`

**目标路径**: `D:\汇度编辑部1\藏经阁\l1\writing_craft\`

**迁移文件清单**:

| 文件名 | 说明 | 状态 |
|--------|------|------|
| expression_base.json | 表达基础规则 | ✅ 已迁移 |
| lighthouse_dailaoban.json | 灯塔风格规则 | ✅ 已迁移 |
| m2_narrative_primitives.json | 叙事原语规则 | ✅ 已迁移 |
| m4_rhetoric_blocks.json | 修辞块规则 | ✅ 已迁移 |
| native_syntax_rules.json | 原生语法规则 | ✅ 已迁移 |
| persona_kernels.json | 人设内核规则 | ✅ 已迁移 |
| register_levels.json | 语体等级规则 | ✅ 已迁移 |
| style_dna_schema.json | 风格DNA模式 | ✅ 已迁移 |

**迁移策略**: 
- 保留原目录结构
- 不删除 V2 原文件（保留兼容副本）
- L1 层正式知识，直接晋升

### 2.2 摄取清单 (staging)

**原路径**: `D:\汇度编辑部1\写作知识库\medical_kb_system_v2\intake\manifests\`

**目标路径**: `D:\汇度编辑部1\藏经阁\staging\intake_manifests\`

**迁移文件清单**:

| 文件名 | 说明 | 状态 |
|--------|------|------|
| batch_registry.json | 批次注册表 | ✅ 已迁移 |
| source_index_schema.json | 来源索引模式 | ✅ 已迁移 |

**迁移策略**:
- 作为中间产物放入 staging 层
- 保留原文件，后续可根据需要晋升

## 3. 兼容性处理

### 3.1 保留原路径

- V2 原目录文件保留，不删除
- 作为过渡期的兼容副本

### 3.2 不做路径切换

- 本轮不修改 V2 运行时读取路径
- 待后续发布物验证后再切换

## 4. 验证清单

- [x] 目标目录已创建
- [x] 文件已复制
- [x] 文件数量匹配
- [x] 原文件保留
- [ ] 发布物生成（Phase 5）
- [ ] 消费验证（Phase 6）

## 5. 后续批次建议

| 批次 | 目录 | 预估文件数 | 目标层 | 建议 |
|------|------|-----------|--------|------|
| Batch 2 | rules/l2_medical_playbook | 9 | L2 | 医学策略层 |
| Batch 3 | structured/l3 | 12 | L3 | 疾病知识层 |
| Batch 4 | structured/l4 | 28 | L4 | 产品证据层 |
| Batch 5 | evidence/ | 67 | raw/staging | 证据库 |

---

**Evidence Summary**:
1. 运行命令: PowerShell Copy-Item
2. 验证: l1/writing_craft 8 files, staging/intake_manifests 2 files
3. 原路径保留: V2 rules/l1_writing_craft/ 和 intake/manifests/ 文件未删除