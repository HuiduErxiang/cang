"""
藏经阁分仓机制 - Python 实现

本模块实现 intake -> raw 分仓机制的核心逻辑：
1. IntakeRecord / SourceRecord / RawAsset 数据结构
2. 盘点流程：文件识别、SHA-256 去重、基础元数据补充
3. 分发逻辑：按优先级仲裁确定目标仓库

遵循 docs/藏经阁分仓机制方案_20260316.md 的规范

@version 1.0
@created 2026-03-16
"""

import hashlib
import json
import mimetypes
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, List, Any


# ============================================
# 枚举定义
# ============================================

class IntakeStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    REVIEWING = "reviewing"
    REVIEWED = "reviewed"
    DISPATCHED = "dispatched"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"


class DepositMethod(str, Enum):
    DROP = "drop"
    UPLOAD = "upload"
    IMPORT = "import"


class SourceChannel(str, Enum):
    USER_UPLOAD = "USER_UPLOAD"
    BATCH_IMPORT = "BATCH_IMPORT"
    SYSTEM_DROP = "SYSTEM_DROP"
    MEDICAL_DATABASE = "MEDICAL_DATABASE"
    PARTNER_SHARED = "PARTNER_SHARED"
    WEB_CRAWLED = "WEB_CRAWLED"
    EDITORIAL = "EDITORIAL"
    EXPERT_INPUT = "EXPERT_INPUT"
    MEETING_NOTES = "MEETING_NOTES"
    V2_HISTORICAL = "V2_HISTORICAL"
    LEGACY_IMPORT = "LEGACY_IMPORT"
    ORPHAN = "ORPHAN"


class SourceStatus(str, Enum):
    RAW = "raw"
    STAGED = "staged"
    DISTILLED = "distilled"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"


# ============================================
# 分仓规则常量
# ============================================

# 来源渠道到仓库路径的映射
SOURCE_CHANNEL_TO_WAREHOUSE = {
    SourceChannel.USER_UPLOAD: "raw/deposited/user_upload/",
    SourceChannel.BATCH_IMPORT: "raw/deposited/batch_import/",
    SourceChannel.SYSTEM_DROP: "raw/deposited/system_drop/",
    SourceChannel.MEDICAL_DATABASE: "raw/external/medical_database/",
    SourceChannel.PARTNER_SHARED: "raw/external/partner_shared/",
    SourceChannel.WEB_CRAWLED: "raw/external/web_crawled/",
    SourceChannel.EDITORIAL: "raw/internal/editorial/",
    SourceChannel.EXPERT_INPUT: "raw/internal/expert_input/",
    SourceChannel.MEETING_NOTES: "raw/internal/meeting_notes/",
    SourceChannel.V2_HISTORICAL: "raw/migrated/v2_historical/",
    SourceChannel.LEGACY_IMPORT: "raw/migrated/legacy_import/",
    SourceChannel.ORPHAN: "raw/orphan/",
}

# 合作方列表
PARTNER_SYSTEMS = ["合作方", "甲方", "药企"]


# ============================================
# 数据结构定义
# ============================================

@dataclass
class InventoryResult:
    """盘点结果"""
    source_key: str
    content_hash: str
    is_duplicate: bool
    file_format: str
    mime_type: str
    duplicate_of: Optional[str] = None
    page_count: Optional[int] = None
    has_ocr: Optional[bool] = None


@dataclass
class ClassificationResult:
    """分类结果"""
    target_warehouse: str
    source_channel: SourceChannel
    confidence: float
    classification_reason: str
    priority_level: int


@dataclass
class IntakeRecord:
    """进货记录"""
    intake_id: str
    status: IntakeStatus
    deposited_at: str
    deposited_by: str
    deposit_method: DepositMethod
    original_filename: str
    file_size_bytes: int
    content_hash: str
    mime_type: str
    inbox_path: str
    original_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    inventory_result: Optional[InventoryResult] = None
    classification_result: Optional[ClassificationResult] = None
    source_key: Optional[str] = None
    batch_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "intake_id": self.intake_id,
            "status": self.status.value,
            "deposited_at": self.deposited_at,
            "deposited_by": self.deposited_by,
            "deposit_method": self.deposit_method.value,
            "original_filename": self.original_filename,
            "file_size_bytes": self.file_size_bytes,
            "content_hash": self.content_hash,
            "mime_type": self.mime_type,
            "inbox_path": self.inbox_path,
        }
        if self.original_path:
            result["original_path"] = self.original_path
        if self.metadata:
            result["metadata"] = self.metadata
        if self.inventory_result:
            result["inventory_result"] = {
                "source_key": self.inventory_result.source_key,
                "content_hash": self.inventory_result.content_hash,
                "is_duplicate": self.inventory_result.is_duplicate,
                "file_format": self.inventory_result.file_format,
                "mime_type": self.inventory_result.mime_type,
            }
        if self.classification_result:
            result["classification_result"] = {
                "target_warehouse": self.classification_result.target_warehouse,
                "source_channel": self.classification_result.source_channel.value,
                "confidence": self.classification_result.confidence,
                "classification_reason": self.classification_result.classification_reason,
                "priority_level": self.classification_result.priority_level,
            }
        if self.source_key:
            result["source_key"] = self.source_key
        if self.batch_id:
            result["batch_id"] = self.batch_id
        return result


@dataclass
class SourceRecord:
    """来源记录"""
    source_key: str
    source_channel: SourceChannel
    warehouse_path: str
    ingested_at: str
    intake_id: str
    source_system: Optional[str] = None
    status: SourceStatus = SourceStatus.RAW
    content_type: Optional[str] = None
    asset_keys: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "source_key": self.source_key,
            "source_channel": self.source_channel.value,
            "warehouse_path": self.warehouse_path,
            "ingested_at": self.ingested_at,
            "status": self.status.value,
            "intake_id": self.intake_id,
            "asset_keys": self.asset_keys,
        }
        if self.source_system:
            result["source_system"] = self.source_system
        if self.content_type:
            result["content_type"] = self.content_type
        return result


# ============================================
# 工具函数
# ============================================

def calculate_content_hash(file_path: str) -> str:
    """
    计算文件内容的 SHA-256 哈希值（取前 16 位）
    
    Args:
        file_path: 文件路径
        
    Returns:
        16 位哈希字符串
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    获取文件基本信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        包含文件大小、MIME 类型等信息的字典
    """
    path = Path(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    
    return {
        "file_size_bytes": path.stat().st_size if path.exists() else 0,
        "mime_type": mime_type or "application/octet-stream",
        "file_format": path.suffix.lstrip(".").upper() or "UNKNOWN",
    }


def generate_intake_id(date_str: Optional[str] = None, sequence: int = 1) -> str:
    """
    生成进货记录 ID
    
    Args:
        date_str: 日期字符串，格式 YYYYMMDD，默认使用当前日期
        sequence: 序号
        
    Returns:
        格式为 INT-YYYYMMDD-XXXX 的 ID
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")
    return f"INT-{date_str}-{sequence:04d}"


def generate_source_key(date_str: Optional[str] = None, sequence: int = 1) -> str:
    """
    生成来源记录 ID
    
    Args:
        date_str: 日期字符串，格式 YYYYMMDD，默认使用当前日期
        sequence: 序号
        
    Returns:
        格式为 SRC-YYYYMMDD-XXXX 的 ID
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")
    return f"SRC-{date_str}-{sequence:04d}"


# ============================================
# 分发逻辑 - 按优先级仲裁
# ============================================

def classify_by_source_channel(
    source_system: Optional[str],
    deposit_method: Optional[str],
    deposited_by_role: Optional[str],
    filename: Optional[str]
) -> ClassificationResult:
    """
    按优先级仲裁确定来源渠道
    
    优先级顺序：
    1. 来源系统标记（最可靠）
    2. 投递方式
    3. 投递者角色
    4. 迁移标记
    5. orphan（兜底）
    
    Args:
        source_system: 来源系统
        deposit_method: 投递方式
        deposited_by_role: 投递者角色
        filename: 文件名
        
    Returns:
        ClassificationResult 包含目标仓库和分类信息
    """
    
    # 第一优先级：来源系统标记
    if source_system:
        if source_system == "医学数据库":
            return ClassificationResult(
                target_warehouse=SOURCE_CHANNEL_TO_WAREHOUSE[SourceChannel.MEDICAL_DATABASE],
                source_channel=SourceChannel.MEDICAL_DATABASE,
                confidence=0.95,
                classification_reason=f"source_system 标记为 '{source_system}'",
                priority_level=1
            )
        if source_system in PARTNER_SYSTEMS:
            return ClassificationResult(
                target_warehouse=SOURCE_CHANNEL_TO_WAREHOUSE[SourceChannel.PARTNER_SHARED],
                source_channel=SourceChannel.PARTNER_SHARED,
                confidence=0.90,
                classification_reason=f"source_system 标记为合作方 '{source_system}'",
                priority_level=1
            )
        if source_system == "网络爬虫":
            return ClassificationResult(
                target_warehouse=SOURCE_CHANNEL_TO_WAREHOUSE[SourceChannel.WEB_CRAWLED],
                source_channel=SourceChannel.WEB_CRAWLED,
                confidence=0.95,
                classification_reason="source_system 标记为 '网络爬虫'",
                priority_level=1
            )
        if source_system == "V2迁移":
            return ClassificationResult(
                target_warehouse=SOURCE_CHANNEL_TO_WAREHOUSE[SourceChannel.V2_HISTORICAL],
                source_channel=SourceChannel.V2_HISTORICAL,
                confidence=0.95,
                classification_reason="source_system 标记为 'V2迁移'",
                priority_level=1
            )
        if "legacy" in source_system.lower() or "遗留" in source_system:
            return ClassificationResult(
                target_warehouse=SOURCE_CHANNEL_TO_WAREHOUSE[SourceChannel.LEGACY_IMPORT],
                source_channel=SourceChannel.LEGACY_IMPORT,
                confidence=0.90,
                classification_reason=f"source_system 标记为遗留 '{source_system}'",
                priority_level=1
            )
    
    # 第二优先级：投递方式
    if deposit_method:
        if deposit_method == "upload":
            return ClassificationResult(
                target_warehouse=SOURCE_CHANNEL_TO_WAREHOUSE[SourceChannel.USER_UPLOAD],
                source_channel=SourceChannel.USER_UPLOAD,
                confidence=0.85,
                classification_reason="deposit_method 为 'upload'",
                priority_level=2
            )
        if deposit_method == "import":
            return ClassificationResult(
                target_warehouse=SOURCE_CHANNEL_TO_WAREHOUSE[SourceChannel.BATCH_IMPORT],
                source_channel=SourceChannel.BATCH_IMPORT,
                confidence=0.85,
                classification_reason="deposit_method 为 'import'",
                priority_level=2
            )
        if deposit_method == "drop":
            return ClassificationResult(
                target_warehouse=SOURCE_CHANNEL_TO_WAREHOUSE[SourceChannel.SYSTEM_DROP],
                source_channel=SourceChannel.SYSTEM_DROP,
                confidence=0.85,
                classification_reason="deposit_method 为 'drop'",
                priority_level=2
            )
    
    # 第三优先级：投递者角色
    if deposited_by_role:
        if deposited_by_role in ["editor", "编辑"]:
            return ClassificationResult(
                target_warehouse=SOURCE_CHANNEL_TO_WAREHOUSE[SourceChannel.EDITORIAL],
                source_channel=SourceChannel.EDITORIAL,
                confidence=0.80,
                classification_reason=f"deposited_by_role 为 '{deposited_by_role}'",
                priority_level=3
            )
        if deposited_by_role in ["expert", "医学专家"]:
            return ClassificationResult(
                target_warehouse=SOURCE_CHANNEL_TO_WAREHOUSE[SourceChannel.EXPERT_INPUT],
                source_channel=SourceChannel.EXPERT_INPUT,
                confidence=0.80,
                classification_reason=f"deposited_by_role 为 '{deposited_by_role}'",
                priority_level=3
            )
    
    # 第三优先级补充：文件名匹配
    if filename:
        if "会议纪要" in filename or "会议记录" in filename:
            return ClassificationResult(
                target_warehouse=SOURCE_CHANNEL_TO_WAREHOUSE[SourceChannel.MEETING_NOTES],
                source_channel=SourceChannel.MEETING_NOTES,
                confidence=0.75,
                classification_reason="文件名包含 '会议纪要' 或 '会议记录'",
                priority_level=3
            )
    
    # 兜底：orphan
    return ClassificationResult(
        target_warehouse=SOURCE_CHANNEL_TO_WAREHOUSE[SourceChannel.ORPHAN],
        source_channel=SourceChannel.ORPHAN,
        confidence=0.50,
        classification_reason="无法判断来源渠道，落入 orphan",
        priority_level=5
    )


# ============================================
# IntakeManager - 进货管理器
# ============================================

class IntakeManager:
    """
    进货管理器 - 负责 intake -> raw 的完整流程
    """
    
    def __init__(self, base_path: str):
        """
        初始化进货管理器
        
        Args:
            base_path: 藏经阁根目录路径
        """
        self.base_path = Path(base_path)
        self.intake_path = self.base_path / "intake"
        self.raw_path = self.base_path / "raw"
        self.lineage_path = self.base_path / "lineage"
        
        # 真相源文件路径
        self.registry_path = self.intake_path / "manifests" / "intake_registry.json"
        self.dedup_path = self.intake_path / "manifests" / "dedup_index.json"
        
        # 加载或初始化注册表
        self._load_registry()
        self._load_dedup_index()
    
    def _load_registry(self):
        """加载进货注册表"""
        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as f:
                self.registry = json.load(f)
        else:
            self.registry = {
                "registry_version": "1.0",
                "created_at": datetime.now().isoformat() + "Z",
                "description": "进货总账",
                "schema_version": "1.0",
                "records": [],
                "statistics": {
                    "total_records": 0,
                    "by_status": {s.value: 0 for s in IntakeStatus},
                    "by_deposit_method": {m.value: 0 for m in DepositMethod},
                    "last_updated": datetime.now().isoformat() + "Z"
                }
            }
    
    def _load_dedup_index(self):
        """加载去重索引"""
        if self.dedup_path.exists():
            with open(self.dedup_path, "r", encoding="utf-8") as f:
                self.dedup_index = json.load(f)
        else:
            self.dedup_index = {
                "index_version": "1.0",
                "created_at": datetime.now().isoformat() + "Z",
                "description": "去重索引",
                "hash_algorithm": "sha256-truncated-16",
                "index": {},
                "statistics": {
                    "total_entries": 0,
                    "total_duplicates_detected": 0,
                    "last_updated": datetime.now().isoformat() + "Z"
                }
            }
    
    def _save_registry(self):
        """保存进货注册表"""
        self.registry["statistics"]["last_updated"] = datetime.now().isoformat() + "Z"
        # 确保目录存在
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)
    
    def _save_dedup_index(self):
        """保存去重索引"""
        self.dedup_index["statistics"]["last_updated"] = datetime.now().isoformat() + "Z"
        # 确保目录存在
        self.dedup_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.dedup_path, "w", encoding="utf-8") as f:
            json.dump(self.dedup_index, f, ensure_ascii=False, indent=2)
    
    def deposit(
        self,
        file_path: str,
        deposited_by: str,
        deposit_method: DepositMethod,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IntakeRecord:
        """
        投递文件到 intake
        
        Args:
            file_path: 文件路径
            deposited_by: 投递者标识
            deposit_method: 投递方式
            metadata: 额外元数据
            
        Returns:
            IntakeRecord 进货记录
        """
        # 获取文件信息
        file_info = get_file_info(file_path)
        content_hash = calculate_content_hash(file_path)
        
        # 生成 ID
        sequence = len(self.registry["records"]) + 1
        intake_id = generate_intake_id(sequence=sequence)
        
        # 确定存储路径
        inbox_subdir = {
            DepositMethod.DROP: "drop",
            DepositMethod.UPLOAD: "upload",
            DepositMethod.IMPORT: "import"
        }[deposit_method]
        
        inbox_path = f"intake/inbox/{inbox_subdir}/{intake_id}{Path(file_path).suffix}"
        full_inbox_path = self.base_path / inbox_path
        
        # 复制文件到 inbox
        full_inbox_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, full_inbox_path)
        
        # 创建进货记录
        record = IntakeRecord(
            intake_id=intake_id,
            status=IntakeStatus.PENDING_REVIEW,
            deposited_at=datetime.now().isoformat() + "Z",
            deposited_by=deposited_by,
            deposit_method=deposit_method,
            original_filename=Path(file_path).name,
            file_size_bytes=file_info["file_size_bytes"],
            content_hash=content_hash,
            mime_type=file_info["mime_type"],
            inbox_path=inbox_path,
            original_path=file_path,
            metadata=metadata or {}
        )
        
        # 添加到注册表
        self.registry["records"].append(record.to_dict())
        self.registry["statistics"]["total_records"] += 1
        self.registry["statistics"]["by_status"]["pending_review"] += 1
        self.registry["statistics"]["by_deposit_method"][deposit_method.value] += 1
        self._save_registry()
        
        return record
    
    def inventory(self, intake_id: str) -> IntakeRecord:
        """
        执行盘点流程
        
        Args:
            intake_id: 进货记录 ID
            
        Returns:
            更新后的 IntakeRecord
        """
        # 查找记录
        record_dict = None
        for r in self.registry["records"]:
            if r["intake_id"] == intake_id:
                record_dict = r
                break
        
        if not record_dict:
            raise ValueError(f"IntakeRecord not found: {intake_id}")
        
        # 更新状态为盘点中
        old_status = record_dict["status"]
        record_dict["status"] = IntakeStatus.REVIEWING.value
        self.registry["statistics"]["by_status"][old_status] -= 1
        self.registry["statistics"]["by_status"]["reviewing"] += 1
        
        content_hash = record_dict["content_hash"]
        
        # 去重检查
        is_duplicate = content_hash in self.dedup_index["index"]
        duplicate_of = None
        if is_duplicate:
            duplicate_of = self.dedup_index["index"][content_hash].get("intake_id")
            record_dict["status"] = IntakeStatus.DUPLICATE.value
            self.registry["statistics"]["by_status"]["reviewing"] -= 1
            self.registry["statistics"]["by_status"]["duplicate"] += 1
            self.dedup_index["statistics"]["total_duplicates_detected"] += 1
            
            # 创建盘点结果（重复文件）
            record_dict["inventory_result"] = {
                "source_key": self.dedup_index["index"][content_hash].get("source_key", ""),
                "content_hash": content_hash,
                "is_duplicate": True,
                "duplicate_of": duplicate_of,
                "file_format": Path(record_dict["original_filename"]).suffix.lstrip(".").upper() or "UNKNOWN",
                "mime_type": record_dict["mime_type"]
            }
        else:
            # 添加到去重索引
            sequence = len(self.dedup_index["index"]) + 1
            source_key = generate_source_key(sequence=sequence)
            
            self.dedup_index["index"][content_hash] = {
                "intake_id": intake_id,
                "source_key": source_key,
                "original_filename": record_dict["original_filename"],
                "file_size_bytes": record_dict["file_size_bytes"],
                "first_seen_at": datetime.now().isoformat() + "Z"
            }
            self.dedup_index["statistics"]["total_entries"] += 1
            
            # 分类判断
            classification = classify_by_source_channel(
                source_system=record_dict.get("metadata", {}).get("source_system"),
                deposit_method=record_dict.get("deposit_method"),
                deposited_by_role=record_dict.get("metadata", {}).get("deposited_by_role"),
                filename=record_dict.get("original_filename")
            )
            
            # 创建盘点结果
            inventory_result = InventoryResult(
                source_key=source_key,
                content_hash=content_hash,
                is_duplicate=False,
                file_format=Path(record_dict["original_filename"]).suffix.lstrip(".").upper() or "UNKNOWN",
                mime_type=record_dict["mime_type"]
            )
            
            record_dict["inventory_result"] = {
                "source_key": inventory_result.source_key,
                "content_hash": inventory_result.content_hash,
                "is_duplicate": inventory_result.is_duplicate,
                "file_format": inventory_result.file_format,
                "mime_type": inventory_result.mime_type
            }
            record_dict["classification_result"] = {
                "target_warehouse": classification.target_warehouse,
                "source_channel": classification.source_channel.value,
                "confidence": classification.confidence,
                "classification_reason": classification.classification_reason,
                "priority_level": classification.priority_level
            }
            record_dict["source_key"] = source_key
            
            # 更新状态为已盘点
            record_dict["status"] = IntakeStatus.REVIEWED.value
            self.registry["statistics"]["by_status"]["reviewing"] -= 1
            self.registry["statistics"]["by_status"]["reviewed"] += 1
        
        self._save_registry()
        self._save_dedup_index()
        
        return IntakeRecord(
            intake_id=record_dict["intake_id"],
            status=IntakeStatus(record_dict["status"]),
            deposited_at=record_dict["deposited_at"],
            deposited_by=record_dict["deposited_by"],
            deposit_method=DepositMethod(record_dict["deposit_method"]),
            original_filename=record_dict["original_filename"],
            file_size_bytes=record_dict["file_size_bytes"],
            content_hash=record_dict["content_hash"],
            mime_type=record_dict["mime_type"],
            inbox_path=record_dict["inbox_path"],
            original_path=record_dict.get("original_path"),
            metadata=record_dict.get("metadata", {}),
            inventory_result=InventoryResult(**record_dict["inventory_result"]) if record_dict.get("inventory_result") else None,
            classification_result=ClassificationResult(
                target_warehouse=record_dict["classification_result"]["target_warehouse"],
                source_channel=SourceChannel(record_dict["classification_result"]["source_channel"]),
                confidence=record_dict["classification_result"]["confidence"],
                classification_reason=record_dict["classification_result"]["classification_reason"],
                priority_level=record_dict["classification_result"]["priority_level"]
            ) if record_dict.get("classification_result") else None,
            source_key=record_dict.get("source_key")
        )
    
    def dispatch(self, intake_id: str) -> SourceRecord:
        """
        执行分发流程
        
        Args:
            intake_id: 进货记录 ID
            
        Returns:
            SourceRecord 来源记录
        """
        # 查找记录
        record_dict = None
        for r in self.registry["records"]:
            if r["intake_id"] == intake_id:
                record_dict = r
                break
        
        if not record_dict:
            raise ValueError(f"IntakeRecord not found: {intake_id}")
        
        if record_dict["status"] != IntakeStatus.REVIEWED.value:
            raise ValueError(f"IntakeRecord must be in 'reviewed' status, current: {record_dict['status']}")
        
        classification = record_dict["classification_result"]
        inventory = record_dict["inventory_result"]
        
        # 构建目标路径
        source_key = inventory["source_key"]
        target_warehouse = classification["target_warehouse"]
        source_channel = SourceChannel(classification["source_channel"])
        
        # 获取文件扩展名
        file_ext = Path(record_dict["original_filename"]).suffix
        target_filename = f"{source_key}{file_ext}"
        warehouse_path = f"{target_warehouse}{target_filename}"
        
        # 移动文件
        src_path = self.base_path / record_dict["inbox_path"]
        dst_path = self.base_path / warehouse_path
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))
        
        # 更新进货记录状态
        record_dict["status"] = IntakeStatus.DISPATCHED.value
        self.registry["statistics"]["by_status"]["reviewed"] -= 1
        self.registry["statistics"]["by_status"]["dispatched"] += 1
        self._save_registry()
        
        # 创建来源记录
        source_record = SourceRecord(
            source_key=source_key,
            source_channel=source_channel,
            warehouse_path=warehouse_path,
            ingested_at=datetime.now().isoformat() + "Z",
            intake_id=intake_id,
            source_system=record_dict.get("metadata", {}).get("source_system"),
            status=SourceStatus.RAW,
            asset_keys=[]
        )
        
        # 保存来源记录
        source_index_path = self.lineage_path / "source_index.json"
        if source_index_path.exists():
            with open(source_index_path, "r", encoding="utf-8") as f:
                source_index = json.load(f)
        else:
            source_index = {
                "index_version": "1.0",
                "created_at": datetime.now().isoformat() + "Z",
                "sources": []
            }
        
        source_index["sources"].append(source_record.to_dict())
        # 确保目录存在
        source_index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(source_index_path, "w", encoding="utf-8") as f:
            json.dump(source_index, f, ensure_ascii=False, indent=2)
        
        # 记录血缘
        self._record_lineage(record_dict, source_record)
        
        return source_record
    
    def _record_lineage(self, intake_record: Dict, source_record: SourceRecord):
        """记录血缘链"""
        intake_chain_path = self.lineage_path / "intake_chain" / "intake_to_source.json"
        
        if intake_chain_path.exists():
            with open(intake_chain_path, "r", encoding="utf-8") as f:
                intake_chain = json.load(f)
        else:
            intake_chain = {
                "chain_version": "1.0",
                "created_at": datetime.now().isoformat() + "Z",
                "chains": []
            }
        
        chain_record = {
            "chain_id": f"CHAIN-{datetime.now().strftime('%Y%m%d')}-{len(intake_chain['chains']) + 1:04d}",
            "intake_id": intake_record["intake_id"],
            "source_key": source_record.source_key,
            "chain_timestamp": datetime.now().isoformat() + "Z",
            "chain_type": "intake_to_source",
            "transformation": {
                "type": "dispatch",
                "from_path": intake_record["inbox_path"],
                "to_path": source_record.warehouse_path
            },
            "metadata_changes": {
                "added": ["source_key", "source_channel"]
            }
        }
        
        intake_chain["chains"].append(chain_record)
        # 确保目录存在
        intake_chain_path.parent.mkdir(parents=True, exist_ok=True)
        with open(intake_chain_path, "w", encoding="utf-8") as f:
            json.dump(intake_chain, f, ensure_ascii=False, indent=2)
        
        # 记录状态变更历史
        status_history_path = self.lineage_path / "status_history" / "intake_status.json"
        
        if status_history_path.exists():
            with open(status_history_path, "r", encoding="utf-8") as f:
                status_history = json.load(f)
        else:
            status_history = {
                "history_version": "1.0",
                "created_at": datetime.now().isoformat() + "Z",
                "records": []
            }
        
        status_record = {
            "object_type": "IntakeRecord",
            "object_id": intake_record["intake_id"],
            "status_history": [
                {
                    "from_status": None,
                    "to_status": "pending_review",
                    "changed_at": intake_record["deposited_at"],
                    "changed_by": intake_record["deposited_by"],
                    "reason": "文件投递"
                },
                {
                    "from_status": "pending_review",
                    "to_status": "reviewed",
                    "changed_at": datetime.now().isoformat() + "Z",
                    "changed_by": "system_auto",
                    "reason": "自动盘点完成"
                },
                {
                    "from_status": "reviewed",
                    "to_status": "dispatched",
                    "changed_at": datetime.now().isoformat() + "Z",
                    "changed_by": "system_auto",
                    "reason": f"自动分发到 {source_record.warehouse_path}"
                }
            ]
        }
        
        status_history["records"].append(status_record)
        # 确保目录存在
        status_history_path.parent.mkdir(parents=True, exist_ok=True)
        with open(status_history_path, "w", encoding="utf-8") as f:
            json.dump(status_history, f, ensure_ascii=False, indent=2)


# ============================================
# 命令行入口
# ============================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python intake_manager.py <command> [args]")
        print("Commands:")
        print("  deposit <file_path> <deposited_by> <deposit_method> [metadata_json]")
        print("  inventory <intake_id>")
        print("  dispatch <intake_id>")
        print("  process <file_path> <deposited_by> <deposit_method> [metadata_json]  # deposit + inventory + dispatch")
        sys.exit(1)
    
    base_path = Path(__file__).parent.parent
    manager = IntakeManager(str(base_path))
    
    command = sys.argv[1]
    
    if command == "deposit":
        if len(sys.argv) < 5:
            print("Usage: python intake_manager.py deposit <file_path> <deposited_by> <deposit_method>")
            sys.exit(1)
        
        file_path = sys.argv[2]
        deposited_by = sys.argv[3]
        deposit_method = DepositMethod(sys.argv[4])
        metadata = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
        
        record = manager.deposit(file_path, deposited_by, deposit_method, metadata)
        print(f"Created IntakeRecord: {record.intake_id}")
        print(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))
    
    elif command == "inventory":
        if len(sys.argv) < 3:
            print("Usage: python intake_manager.py inventory <intake_id>")
            sys.exit(1)
        
        intake_id = sys.argv[2]
        record = manager.inventory(intake_id)
        print(f"Inventory completed: {record.intake_id}")
        print(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))
    
    elif command == "dispatch":
        if len(sys.argv) < 3:
            print("Usage: python intake_manager.py dispatch <intake_id>")
            sys.exit(1)
        
        intake_id = sys.argv[2]
        source = manager.dispatch(intake_id)
        print(f"Dispatched to: {source.warehouse_path}")
        print(json.dumps(source.to_dict(), ensure_ascii=False, indent=2))
    
    elif command == "process":
        if len(sys.argv) < 5:
            print("Usage: python intake_manager.py process <file_path> <deposited_by> <deposit_method> [metadata_json]")
            sys.exit(1)
        
        file_path = sys.argv[2]
        deposited_by = sys.argv[3]
        deposit_method = DepositMethod(sys.argv[4])
        metadata = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
        
        # 完整流程：deposit -> inventory -> dispatch
        record = manager.deposit(file_path, deposited_by, deposit_method, metadata)
        print(f"1. Deposit: {record.intake_id}")
        
        record = manager.inventory(record.intake_id)
        print(f"2. Inventory: {record.status.value}")
        
        if record.status == IntakeStatus.REVIEWED:
            source = manager.dispatch(record.intake_id)
            print(f"3. Dispatch: {source.warehouse_path}")
            print("\nFinal result:")
            print(json.dumps(source.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"3. Skipped dispatch (status: {record.status.value})")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)