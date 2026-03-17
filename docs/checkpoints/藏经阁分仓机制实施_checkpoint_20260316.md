# 藏经阁分仓机制实施 Checkpoint

> **批次**: Batch-1 (2026-03-16)
> **执行边界**: `docs/藏经阁分仓机制方案_20260316.md`
> **状态**: ✅ 已完成

---

## 当前批次目标

实现可运行的最小闭环：
- intake/ 目录骨架与 manifests 真相源
- IntakeRecord / SourceRecord / RawAsset 数据结构与状态流转
- 盘点流程：文件识别、SHA-256 去重、基础元数据补充
- 分发逻辑：按优先级仲裁
- lineage 的 intake_chain、status_history、source_index
- staging/intake_manifests 的迁移/废弃标记

---

## 已完成项

### 1. 目录结构创建 ✅

**证据**：
- `intake/` 目录已创建，包含 `inbox/drop`、`inbox/upload`、`inbox/import`、`staging`、`reviewed`、`rejected`、`manifests/`
- `raw/` 目录已按来源渠道重组，包含 `deposited/`、`external/`、`internal/`、`migrated/`、`orphan/` 及子目录
- `lineage/` 扩展目录已创建，包含 `intake_chain/`、`status_history/`、`distillation_chain/`

**验证命令**：
```powershell
ls D:\汇度编辑部1\藏经阁\intake\
ls D:\汇度编辑部1\藏经阁\raw\
ls D:\汇度编辑部1\藏经阁\lineage\
```

### 2. 真相源文件创建 ✅

**证据**：
- `intake/manifests/intake_registry.json` - 进货总账（空初始化）
- `intake/manifests/dedup_index.json` - 去重索引（空初始化）
- `intake/manifests/schemas/intake_record_schema.json` - 数据规范定义

**文件路径**：
- `D:\汇度编辑部1\藏经阁\intake\manifests\intake_registry.json`
- `D:\汇度编辑部1\藏经阁\intake\manifests\dedup_index.json`

### 3. 数据结构定义 ✅

**证据**：
- `tools/types.ts` - TypeScript 类型定义（IntakeRecord、SourceRecord、RawAsset、ClassificationResult 等）
- `tools/intake_manager.py` - Python 数据模型实现

**文件路径**：
- `D:\汇度编辑部1\藏经阁\tools\types.ts`
- `D:\汇度编辑部1\藏经阁\tools\intake_manager.py`

### 4. 盘点工具实现 ✅

**证据**：
- `intake_manager.py` 中的 `calculate_content_hash()` - SHA-256 哈希计算（取前 16 位）
- `intake_manager.py` 中的 `get_file_info()` - 文件信息获取（大小、MIME 类型）
- `intake_manager.py` 中的 `IntakeManager.inventory()` - 去重检查、分类判断

**关键函数**：
```python
def calculate_content_hash(file_path: str) -> str  # SHA-256 前 16 位
def get_file_info(file_path: str) -> Dict[str, Any]  # 文件信息
def classify_by_source_channel(...) -> ClassificationResult  # 分发分类
```

### 5. 分发逻辑实现 ✅

**证据**：
- `intake_manager.py` 中的 `classify_by_source_channel()` - 按优先级仲裁
- 优先级顺序：来源系统(1) > 投递方式(2) > 投递者角色(3) > 迁移标记(4) > orphan(5)
- `SOURCE_CHANNEL_TO_WAREHOUSE` 常量定义了 12 种来源渠道对应的仓库路径

**关键逻辑**：
```python
# 第一优先级：来源系统标记
if source_system == "医学数据库": -> raw/external/medical_database/
if source_system in PARTNER_SYSTEMS: -> raw/external/partner_shared/
if source_system == "网络爬虫": -> raw/external/web_crawled/
if source_system == "V2迁移": -> raw/migrated/v2_historical/

# 第二优先级：投递方式
if deposit_method == "upload": -> raw/deposited/user_upload/
if deposit_method == "import": -> raw/deposited/batch_import/
if deposit_method == "drop": -> raw/deposited/system_drop/

# ... 第三、四优先级 ...

# 兜底：orphan
return raw/orphan/
```

### 6. 血缘记录实现 ✅

**证据**：
- `lineage/intake_chain/intake_to_source.json` - 初始化完成
- `lineage/status_history/intake_status.json` - 初始化完成
- `lineage/status_history/source_status.json` - 初始化完成
- `lineage/source_index.json` - 统一来源索引初始化完成
- `intake_manager.py` 中的 `_record_lineage()` 方法实现血缘记录

**文件路径**：
- `D:\汇度编辑部1\藏经阁\lineage\intake_chain\intake_to_source.json`
- `D:\汇度编辑部1\藏经阁\lineage\status_history\intake_status.json`
- `D:\汇度编辑部1\藏经阁\lineage\source_index.json`

### 7. staging/intake_manifests 迁移 ✅

**证据**：
- `batch_registry.json` 已复制到 `intake/manifests/legacy_batches/`
- `staging/intake_manifests/README.md` 已创建，明确说明目录已废弃

**文件路径**：
- `D:\汇度编辑部1\藏经阁\intake\manifests\legacy_batches\batch_registry.json`
- `D:\汇度编辑部1\藏经阁\staging\intake_manifests\README.md`

---

## 未完成项

### 待下一批次

1. **CLI 工具完善** - 增强命令行参数处理和错误提示
2. **现有 raw/ 资料迁移** - 将现有 `raw/pdf/` 和 `raw/evidence/` 下的文件按新结构重组
3. **PDF 页数检测** - 增强 `get_file_info()` 支持 PDF 页数统计
4. **配置文件** - 将 PARTNER_SYSTEMS 等常量移至配置文件
5. **边界条件测试** - 文件不存在、权限错误、并发安全等异常场景

---

## 失败项

无

---

## 下一步

1. 使用 `python tools/intake_manager.py process <file> <user> upload` 测试端到端流程
2. 规划现有 raw/ 资料的历史迁移策略
3. 补充边界条件测试用例

---

## 证据路径汇总

| 项目 | 文件路径 |
|------|----------|
| 目录结构 | `intake/`, `raw/`, `lineage/` |
| 进货总账 | `intake/manifests/intake_registry.json` |
| 去重索引 | `intake/manifests/dedup_index.json` |
| 数据规范 | `intake/manifests/schemas/intake_record_schema.json` |
| TypeScript 类型 | `tools/types.ts` |
| Python 实现 | `tools/intake_manager.py` |
| 单元测试 | `tools/test_intake_manager.py` |
| 血缘链 | `lineage/intake_chain/intake_to_source.json` |
| 状态历史 | `lineage/status_history/intake_status.json` |
| 来源索引 | `lineage/source_index.json` |
| 废弃标记 | `staging/intake_manifests/README.md` |
| 历史批次 | `intake/manifests/legacy_batches/batch_registry.json` |

---

## Fix Findings (2026-03-16)

### 清理项

| 项目 | 操作 | 原因 |
|------|------|------|
| `publish/current/current_meta.json` | ✅ 已恢复到批次前状态 | 误删，该文件不属于本次实现边界但应保留 |
| `tools/__pycache__/intake_manager.cpython-314.pyc` | ✅ 已删除 | 运行生成物，不应留在交付面 |

### 证据

**恢复验证**：
```powershell
Test-Path D:\汇度编辑部1\藏经阁\publish\current\current_meta.json  # True
git diff -- "publish/current/current_meta.json"  # 无输出（与 HEAD 一致）
```

**删除验证**：
```powershell
Test-Path D:\汇度编辑部1\藏经阁\tools\__pycache__\intake_manager.cpython-314.pyc  # False
```

---

## Batch 2: 单元测试补充 (2026-03-16)

### 新增文件

| 文件 | 说明 |
|------|------|
| `tools/test_intake_manager.py` | 单元测试文件，覆盖核心功能 |

### 测试覆盖

| 测试类 | 测试数 | 覆盖功能 |
|--------|--------|----------|
| `TestHashCalculation` | 4 | SHA-256 哈希计算（长度、一致性、唯一性、正确性） |
| `TestIDGeneration` | 4 | ID 生成（格式、零填充、默认日期） |
| `TestClassification` | 15 | 优先级仲裁（5个优先级 + 覆盖测试） |
| `TestFullWorkflow` | 6 | 完整流程（deposit/inventory/dispatch/去重/持久化） |
| `TestWarehouseMapping` | 2 | 仓库映射完整性 |

### 测试执行结果

```
Ran 31 tests in 0.101s

OK
```

### 修复项

在测试过程中发现并修复了以下问题：

| 问题 | 修复 |
|------|------|
| `_save_registry` 未创建父目录 | 添加 `mkdir(parents=True, exist_ok=True)` |
| `_save_dedup_index` 未创建父目录 | 添加 `mkdir(parents=True, exist_ok=True)` |
| `dispatch` 写入 `source_index.json` 时未创建目录 | 添加目录创建 |
| `_record_lineage` 写入血缘文件时未创建目录 | 添加目录创建 |
| 重复文件检测后 `inventory_result` 未设置 | 添加重复文件的 `inventory_result` |

### 验证

```powershell
# 运行测试
Set-Location D:\汇度编辑部1\藏经阁\tools
python -m unittest test_intake_manager -v

# 清理 __pycache__
Remove-Item D:\汇度编辑部1\藏经阁\tools\__pycache__ -Recurse -Force
```

---

## Batch 3: 真实文件试跑 (2026-03-16)

### 完成项

| 项目 | 结果 |
|------|------|
| 处理 PDF 数量 | 11 个 |
| 成功分发 | 11 个 |
| 重复检测 | 0 个 |
| 失败 | 0 个 |

### 参数

- `deposited_by`: `codex_real_trial`
- `deposit_method`: `import`
- `source_system`: `药企`
- 分类结果: `PARTNER_SHARED` (优先级 1)
- 目标仓库: `raw/external/partner_shared/`

### Evidence Summary

1. **文件落位验证**: `raw/external/partner_shared/` 下存在 11 个 `SRC-20260316-0001~0011.pdf`
2. **进货总账验证**: `intake/manifests/intake_registry.json` 包含 11 条记录，全部状态为 `dispatched`
3. **血缘记录验证**: `lineage/intake_chain/intake_to_source.json` 包含 11 条血缘链

### 源文件列表

```
D:\汇度编辑部1\项目文章\2026项目表\礼来\礼来资料包\玛仕度肽和替尔泊肽学习资料\
├── GIP减少GLP-1的不良反应.pdf      -> SRC-20260316-0001.pdf
├── GIP协同增效.pdf                  -> SRC-20260316-0002.pdf
├── GIP在白色脂肪中的作用.pdf        -> SRC-20260316-0003.pdf
├── GIP早期研究.pdf                  -> SRC-20260316-0004.pdf
├── GIP激动剂与拮抗剂均能观察到体重减轻.pdf -> SRC-20260316-0005.pdf
├── SURMOUNT-1 DXA.pdf               -> SRC-20260316-0006.pdf
├── SURMOUNT-1研究.pdf               -> SRC-20260316-0007.pdf
├── SURMOUNT-5研究.pdf               -> SRC-20260316-0008.pdf
├── SURPASS-3 MRI.pdf                -> SRC-20260316-0009.pdf
├── 国际肠抑胃素和肠促胰素研究的先驱+北平协和医学院林可胜教授.pdf -> SRC-20260316-0010.pdf
└── 玛仕度肽的天然构体OXM是什么.pdf  -> SRC-20260316-0011.pdf
```

### 失败项

无

### 清理项

- 已删除临时脚本 `tools/batch_import_trial.py`
- 已清理 `tools/__pycache__/`

---

> **Checkpoint 版本**: v1.4
> **最后更新**: 2026-03-16
> **执行者**: AI Assistant
