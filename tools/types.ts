/**
 * 藏经阁分仓机制 - 数据类型定义
 * 
 * 本文件定义 IntakeRecord、SourceRecord、RawAsset 等核心数据结构
 * 遵循 docs/藏经阁分仓机制方案_20260316.md 的规范
 * 
 * @version 1.0
 * @created 2026-03-16
 */

// ============================================
// IntakeRecord - 进货记录
// ============================================

export type IntakeStatus = 
  | 'pending_review'    // 待盘点
  | 'reviewing'         // 盘点中
  | 'reviewed'          // 已盘点待分发
  | 'dispatched'        // 已分发入仓
  | 'rejected'          // 已拒绝
  | 'duplicate';        // 重复已跳过

export type DepositMethod = 'drop' | 'upload' | 'import';

export interface IntakeRecord {
  // 唯一标识
  intake_id: string;           // INT-{YYYYMMDD}-{序号}
  
  // 投递信息
  deposited_at: string;        // ISO 时间戳
  deposited_by: string;        // 投递者标识
  deposit_method: DepositMethod;
  original_filename: string;
  original_path?: string;      // 原始来源路径
  
  // 文件信息
  file_size_bytes: number;
  content_hash: string;        // SHA-256 前 16 位
  mime_type: string;
  inbox_path: string;          // 在 inbox 中的存储路径
  
  // 状态
  status: IntakeStatus;
  
  // 投递时携带的元数据
  metadata?: {
    suggested_category?: string;
    source_system?: string;
    tags?: string[];
    deposited_by_role?: string;
  };
  
  // 盘点结果（盘点后填充）
  inventory_result?: InventoryResult;
  
  // 分类结果（盘点后填充）
  classification_result?: ClassificationResult;
  
  // 关联
  source_key?: string;         // 关联的来源记录
  batch_id?: string;           // 所属批次
}

// ============================================
// InventoryResult - 盘点结果
// ============================================

export interface InventoryResult {
  source_key: string;          // SRC-{YYYYMMDD}-{序号}
  content_hash: string;
  is_duplicate: boolean;
  duplicate_of?: string;       // 如果重复，指向原始文件的 intake_id
  file_format: string;
  mime_type: string;
  page_count?: number;
  has_ocr?: boolean;
}

// ============================================
// ClassificationResult - 分类结果
// ============================================

export type SourceChannel = 
  | 'USER_UPLOAD'
  | 'BATCH_IMPORT'
  | 'SYSTEM_DROP'
  | 'MEDICAL_DATABASE'
  | 'PARTNER_SHARED'
  | 'WEB_CRAWLED'
  | 'EDITORIAL'
  | 'EXPERT_INPUT'
  | 'MEETING_NOTES'
  | 'V2_HISTORICAL'
  | 'LEGACY_IMPORT'
  | 'ORPHAN';

export interface ClassificationResult {
  target_warehouse: string;    // 目标仓库路径
  source_channel: SourceChannel;
  confidence: number;          // 0-1
  classification_reason: string;
  priority_level: number;      // 匹配的优先级（1-5）
}

// ============================================
// SourceRecord - 来源记录
// ============================================

export type SourceStatus = 
  | 'raw'           // 原始状态，刚入仓
  | 'staged'        // 已进入 staging/ 开始蒸馏
  | 'distilled'     // 已完成蒸馏
  | 'archived'      // 已归档
  | 'superseded';   // 已被新版本取代

export type ContentType = 
  | 'CLINICAL_TRIAL'
  | 'GUIDELINE'
  | 'CONSENSUS'
  | 'REFERENCE'
  | 'CONFERENCE'
  | 'REAL_WORLD'
  | 'UNKNOWN';

export interface SourceRecord {
  // 唯一标识
  source_key: string;          // SRC-{YYYYMMDD}-{序号}
  
  // 来源信息（进货阶段确定）
  source_channel: SourceChannel;  // 来源渠道（分仓维度）
  source_system?: string;         // 来源系统
  
  // 入仓信息
  warehouse_path: string;      // 在 raw/ 下的路径
  ingested_at: string;
  
  // 状态
  status: SourceStatus;
  
  // 内容类型标记（蒸馏环节补充）
  content_type?: ContentType;
  
  // 关联
  intake_id: string;           // 来源进货记录
  asset_keys: string[];        // 关联的资产
}

// ============================================
// RawAsset - 原始资产
// ============================================

export type AssetStatus = 'raw' | 'extracting' | 'extracted' | 'archived';

export interface AssetMetadata {
  // 进货阶段产出（基础元数据）
  title?: string;              // 从文件名推断
  original_filename?: string;
  file_size_bytes?: number;
  deposited_by?: string;
  source_system?: string;
  tags?: string[];
  
  // 蒸馏环节补充（领域元数据）
  authors?: string[];
  publication_year?: number;
  disease_area?: string;
  product?: string;
  evidence_level?: string;
  content_type?: string;
}

export interface RawAsset {
  // 唯一标识
  asset_key: string;           // AST-{TYPE}-{序号}
  
  // 存储信息
  storage_path: string;        // 物理存储路径
  content_hash: string;
  
  // 来源
  source_key: string;
  
  // 元数据
  metadata: AssetMetadata;
  
  // 状态
  status: AssetStatus;
}

// ============================================
// IntakeBatch - 进货批次
// ============================================

export interface IntakeBatch {
  batch_id: string;            // BATCH-{YYYY}-{MM}-{序号}
  status: 'pending' | 'processing' | 'completed' | 'partial' | 'failed';
  created_at: string;
  created_by: string;
  source_count: number;
  asset_count: number;
  manifest_path: string;
  storage_zone: string;
  batch_type?: string;
}

// ============================================
// LineageChain - 血缘链记录
// ============================================

export interface LineageChainRecord {
  chain_id: string;            // CHAIN-{YYYYMMDD}-{序号}
  chain_type: 'intake_to_source' | 'source_to_asset';
  chain_timestamp: string;
  
  // intake_to_source
  intake_id?: string;
  source_key?: string;
  
  // source_to_asset
  asset_key?: string;
  
  // 变换信息
  transformation: {
    type: 'dispatch' | 'extract';
    from_path: string;
    to_path: string;
  };
  
  // 元数据变更
  metadata_changes?: {
    added?: string[];
    enriched_later?: string[];
  };
}

// ============================================
// StatusHistory - 状态变更历史
// ============================================

export interface StatusChangeRecord {
  object_type: 'IntakeRecord' | 'SourceRecord' | 'RawAsset';
  object_id: string;
  status_history: Array<{
    from_status: string | null;
    to_status: string;
    changed_at: string;
    changed_by: string;
    reason: string;
  }>;
}

// ============================================
// 分类规则常量
// ============================================

export const CLASSIFICATION_PRIORITIES = {
  1: '来源系统标记（最可靠）',
  2: '投递方式',
  3: '投递者角色',
  4: '迁移标记',
  5: 'orphan（兜底）'
} as const;

export const SOURCE_CHANNEL_TO_WAREHOUSE: Record<SourceChannel, string> = {
  'USER_UPLOAD': 'raw/deposited/user_upload/',
  'BATCH_IMPORT': 'raw/deposited/batch_import/',
  'SYSTEM_DROP': 'raw/deposited/system_drop/',
  'MEDICAL_DATABASE': 'raw/external/medical_database/',
  'PARTNER_SHARED': 'raw/external/partner_shared/',
  'WEB_CRAWLED': 'raw/external/web_crawled/',
  'EDITORIAL': 'raw/internal/editorial/',
  'EXPERT_INPUT': 'raw/internal/expert_input/',
  'MEETING_NOTES': 'raw/internal/meeting_notes/',
  'V2_HISTORICAL': 'raw/migrated/v2_historical/',
  'LEGACY_IMPORT': 'raw/migrated/legacy_import/',
  'ORPHAN': 'raw/orphan/'
};