# 本目录已废弃

> **废弃日期**: 2026-03-16
> **迁移目标**: `intake/manifests/`

## 说明

此目录已废弃，不再作为进货记录的真相源。

### 文件迁移情况

| 原文件 | 迁移目标 | 状态 |
|--------|----------|------|
| `batch_registry.json` | `intake/manifests/legacy_batches/batch_registry.json` | ✅ 已迁移 |
| `source_index_schema.json` | - | ❌ 已废弃（规范已过时） |

### 新的真相源位置

所有新的进货记录统一在以下位置：

```
intake/manifests/
├── intake_registry.json       # 进货总账（真相源）
├── dedup_index.json           # 去重索引
├── schemas/                   # 数据规范
│   └── intake_record_schema.json
├── legacy_batches/            # 历史批次记录（只读归档）
│   └── batch_registry.json
└── intake_batches/            # 新批次记录
```

## 不要在此目录创建新文件

此目录仅作为历史归档保留，请勿在此创建或修改任何文件。

---

**文档版本**: v1.0
**最后更新**: 2026-03-16