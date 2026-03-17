#!/usr/bin/env python
"""
藏经阁分仓机制 - 单元测试

本测试模块覆盖 intake_manager.py 的核心功能：
1. calculate_content_hash - SHA-256 哈希计算
2. generate_intake_id / generate_source_key - ID 生成
3. classify_by_source_channel - 优先级仲裁
4. deposit -> inventory -> dispatch - 最小闭环

所有测试在临时目录中执行，不污染仓库数据。

@version 1.0
@created 2026-03-16
"""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# 添加 tools 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from intake_manager import (
    IntakeManager,
    IntakeStatus,
    DepositMethod,
    SourceChannel,
    SourceStatus,
    InventoryResult,
    ClassificationResult,
    IntakeRecord,
    SourceRecord,
    calculate_content_hash,
    get_file_info,
    generate_intake_id,
    generate_source_key,
    classify_by_source_channel,
    SOURCE_CHANNEL_TO_WAREHOUSE,
    PARTNER_SYSTEMS,
)


class TestHashCalculation(unittest.TestCase):
    """测试 SHA-256 哈希计算"""

    def test_hash_length(self):
        """哈希值长度应为 16"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('test content')
            test_file = f.name
        try:
            hash_result = calculate_content_hash(test_file)
            self.assertEqual(len(hash_result), 16, "Hash should be 16 characters")
        finally:
            os.unlink(test_file)

    def test_hash_consistency(self):
        """相同内容应产生相同哈希"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('identical content')
            test_file1 = f.name
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('identical content')
            test_file2 = f.name
        try:
            hash1 = calculate_content_hash(test_file1)
            hash2 = calculate_content_hash(test_file2)
            self.assertEqual(hash1, hash2, "Same content should produce same hash")
        finally:
            os.unlink(test_file1)
            os.unlink(test_file2)

    def test_hash_uniqueness(self):
        """不同内容应产生不同哈希"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('content A')
            test_file1 = f.name
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('content B')
            test_file2 = f.name
        try:
            hash1 = calculate_content_hash(test_file1)
            hash2 = calculate_content_hash(test_file2)
            self.assertNotEqual(hash1, hash2, "Different content should produce different hash")
        finally:
            os.unlink(test_file1)
            os.unlink(test_file2)

    def test_hash_matches_sha256(self):
        """哈希应匹配 SHA-256 前 16 位"""
        content = b'test content for verification'
        expected_hash = hashlib.sha256(content).hexdigest()[:16]
        
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(content)
            test_file = f.name
        try:
            actual_hash = calculate_content_hash(test_file)
            self.assertEqual(actual_hash, expected_hash, "Hash should match SHA-256 first 16 chars")
        finally:
            os.unlink(test_file)


class TestIDGeneration(unittest.TestCase):
    """测试 ID 生成"""

    def test_intake_id_format(self):
        """Intake ID 格式应为 INT-YYYYMMDD-XXXX"""
        intake_id = generate_intake_id('20260316', 1)
        self.assertTrue(intake_id.startswith('INT-'), "Should start with INT-")
        parts = intake_id.split('-')
        self.assertEqual(len(parts), 3, "Should have 3 parts")
        self.assertEqual(parts[1], '20260316', "Date part should match")
        self.assertEqual(parts[2], '0001', "Sequence should be zero-padded")

    def test_source_key_format(self):
        """Source Key 格式应为 SRC-YYYYMMDD-XXXX"""
        source_key = generate_source_key('20260316', 1)
        self.assertTrue(source_key.startswith('SRC-'), "Should start with SRC-")
        parts = source_key.split('-')
        self.assertEqual(len(parts), 3, "Should have 3 parts")
        self.assertEqual(parts[1], '20260316', "Date part should match")
        self.assertEqual(parts[2], '0001', "Sequence should be zero-padded")

    def test_sequence_zero_padding(self):
        """序号应零填充到 4 位"""
        intake_id = generate_intake_id('20260316', 42)
        self.assertEqual(intake_id, 'INT-20260316-0042', "Sequence should be zero-padded")

    def test_default_date(self):
        """未指定日期时应使用当前日期"""
        from datetime import datetime
        intake_id = generate_intake_id(sequence=1)
        today = datetime.now().strftime('%Y%m%d')
        self.assertIn(today, intake_id, "Should use today's date")


class TestClassification(unittest.TestCase):
    """测试分类逻辑（优先级仲裁）"""

    # ========== 第一优先级：来源系统标记 ==========

    def test_priority1_medical_database(self):
        """医学数据库 -> raw/external/medical_database/"""
        result = classify_by_source_channel('医学数据库', None, None, None)
        self.assertEqual(result.source_channel, SourceChannel.MEDICAL_DATABASE)
        self.assertEqual(result.target_warehouse, 'raw/external/medical_database/')
        self.assertEqual(result.priority_level, 1)

    def test_priority1_partner_shared(self):
        """合作方 -> raw/external/partner_shared/"""
        for partner in PARTNER_SYSTEMS:
            result = classify_by_source_channel(partner, None, None, None)
            self.assertEqual(result.source_channel, SourceChannel.PARTNER_SHARED)
            self.assertEqual(result.target_warehouse, 'raw/external/partner_shared/')
            self.assertEqual(result.priority_level, 1)

    def test_priority1_web_crawled(self):
        """网络爬虫 -> raw/external/web_crawled/"""
        result = classify_by_source_channel('网络爬虫', None, None, None)
        self.assertEqual(result.source_channel, SourceChannel.WEB_CRAWLED)
        self.assertEqual(result.target_warehouse, 'raw/external/web_crawled/')
        self.assertEqual(result.priority_level, 1)

    def test_priority1_v2_historical(self):
        """V2迁移 -> raw/migrated/v2_historical/"""
        result = classify_by_source_channel('V2迁移', None, None, None)
        self.assertEqual(result.source_channel, SourceChannel.V2_HISTORICAL)
        self.assertEqual(result.target_warehouse, 'raw/migrated/v2_historical/')
        self.assertEqual(result.priority_level, 1)

    def test_priority1_legacy_import(self):
        """遗留 -> raw/migrated/legacy_import/"""
        result = classify_by_source_channel('legacy_import', None, None, None)
        self.assertEqual(result.source_channel, SourceChannel.LEGACY_IMPORT)
        self.assertEqual(result.target_warehouse, 'raw/migrated/legacy_import/')
        self.assertEqual(result.priority_level, 1)

        result = classify_by_source_channel('遗留数据', None, None, None)
        self.assertEqual(result.source_channel, SourceChannel.LEGACY_IMPORT)

    # ========== 第二优先级：投递方式 ==========

    def test_priority2_user_upload(self):
        """upload -> raw/deposited/user_upload/"""
        result = classify_by_source_channel(None, 'upload', None, None)
        self.assertEqual(result.source_channel, SourceChannel.USER_UPLOAD)
        self.assertEqual(result.target_warehouse, 'raw/deposited/user_upload/')
        self.assertEqual(result.priority_level, 2)

    def test_priority2_batch_import(self):
        """import -> raw/deposited/batch_import/"""
        result = classify_by_source_channel(None, 'import', None, None)
        self.assertEqual(result.source_channel, SourceChannel.BATCH_IMPORT)
        self.assertEqual(result.target_warehouse, 'raw/deposited/batch_import/')
        self.assertEqual(result.priority_level, 2)

    def test_priority2_system_drop(self):
        """drop -> raw/deposited/system_drop/"""
        result = classify_by_source_channel(None, 'drop', None, None)
        self.assertEqual(result.source_channel, SourceChannel.SYSTEM_DROP)
        self.assertEqual(result.target_warehouse, 'raw/deposited/system_drop/')
        self.assertEqual(result.priority_level, 2)

    # ========== 第三优先级：投递者角色 ==========

    def test_priority3_editorial(self):
        """editor -> raw/internal/editorial/"""
        result = classify_by_source_channel(None, None, 'editor', None)
        self.assertEqual(result.source_channel, SourceChannel.EDITORIAL)
        self.assertEqual(result.target_warehouse, 'raw/internal/editorial/')
        self.assertEqual(result.priority_level, 3)

        result = classify_by_source_channel(None, None, '编辑', None)
        self.assertEqual(result.source_channel, SourceChannel.EDITORIAL)

    def test_priority3_expert_input(self):
        """expert -> raw/internal/expert_input/"""
        result = classify_by_source_channel(None, None, 'expert', None)
        self.assertEqual(result.source_channel, SourceChannel.EXPERT_INPUT)
        self.assertEqual(result.target_warehouse, 'raw/internal/expert_input/')
        self.assertEqual(result.priority_level, 3)

        result = classify_by_source_channel(None, None, '医学专家', None)
        self.assertEqual(result.source_channel, SourceChannel.EXPERT_INPUT)

    def test_priority3_meeting_notes_by_filename(self):
        """会议纪要 -> raw/internal/meeting_notes/"""
        result = classify_by_source_channel(None, None, None, '会议纪要.pdf')
        self.assertEqual(result.source_channel, SourceChannel.MEETING_NOTES)
        self.assertEqual(result.target_warehouse, 'raw/internal/meeting_notes/')
        self.assertEqual(result.priority_level, 3)

        result = classify_by_source_channel(None, None, None, '项目会议记录.docx')
        self.assertEqual(result.source_channel, SourceChannel.MEETING_NOTES)

    # ========== 兜底：orphan ==========

    def test_priority5_orphan(self):
        """无法判断 -> raw/orphan/"""
        result = classify_by_source_channel(None, None, None, None)
        self.assertEqual(result.source_channel, SourceChannel.ORPHAN)
        self.assertEqual(result.target_warehouse, 'raw/orphan/')
        self.assertEqual(result.priority_level, 5)

    # ========== 优先级覆盖测试 ==========

    def test_priority_override_source_over_method(self):
        """来源系统（优先级1）应覆盖投递方式（优先级2）"""
        result = classify_by_source_channel('医学数据库', 'upload', None, None)
        self.assertEqual(result.priority_level, 1, "Priority 1 should override priority 2")
        self.assertEqual(result.source_channel, SourceChannel.MEDICAL_DATABASE)

    def test_priority_override_source_over_role(self):
        """来源系统（优先级1）应覆盖投递者角色（优先级3）"""
        result = classify_by_source_channel('V2迁移', None, 'editor', None)
        self.assertEqual(result.priority_level, 1, "Priority 1 should override priority 3")
        self.assertEqual(result.source_channel, SourceChannel.V2_HISTORICAL)

    def test_priority_override_method_over_role(self):
        """投递方式（优先级2）应覆盖投递者角色（优先级3）"""
        result = classify_by_source_channel(None, 'upload', 'editor', None)
        self.assertEqual(result.priority_level, 2, "Priority 2 should override priority 3")
        self.assertEqual(result.source_channel, SourceChannel.USER_UPLOAD)


class TestFullWorkflow(unittest.TestCase):
    """测试完整工作流：deposit -> inventory -> dispatch"""

    def setUp(self):
        """创建临时目录作为测试仓库"""
        self.temp_dir = tempfile.mkdtemp(prefix='intake_test_')
        self.manager = IntakeManager(self.temp_dir)

    def tearDown(self):
        """清理临时目录"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_deposit_creates_record(self):
        """deposit 应创建进货记录"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, 'test.pdf')
        with open(test_file, 'w') as f:
            f.write('test content')

        # 执行 deposit
        record = self.manager.deposit(
            file_path=test_file,
            deposited_by='test_user',
            deposit_method=DepositMethod.UPLOAD,
            metadata={'source_system': '医学数据库'}
        )

        # 验证
        self.assertIsNotNone(record.intake_id)
        self.assertTrue(record.intake_id.startswith('INT-'))
        self.assertEqual(record.status, IntakeStatus.PENDING_REVIEW)
        self.assertEqual(record.deposited_by, 'test_user')
        self.assertEqual(record.deposit_method, DepositMethod.UPLOAD)
        self.assertEqual(record.original_filename, 'test.pdf')

    def test_inventory_detects_duplicate(self):
        """inventory 应检测重复文件"""
        # 创建两个相同内容的文件
        content = 'duplicate test content'
        test_file1 = os.path.join(self.temp_dir, 'test1.pdf')
        test_file2 = os.path.join(self.temp_dir, 'test2.pdf')
        with open(test_file1, 'w') as f:
            f.write(content)
        with open(test_file2, 'w') as f:
            f.write(content)

        # 投递第一个文件并盘点
        record1 = self.manager.deposit(test_file1, 'user1', DepositMethod.UPLOAD)
        record1 = self.manager.inventory(record1.intake_id)
        self.assertEqual(record1.status, IntakeStatus.REVIEWED)
        self.assertFalse(record1.inventory_result.is_duplicate)

        # 投递第二个文件并盘点
        record2 = self.manager.deposit(test_file2, 'user2', DepositMethod.UPLOAD)
        record2 = self.manager.inventory(record2.intake_id)
        self.assertEqual(record2.status, IntakeStatus.DUPLICATE)
        self.assertTrue(record2.inventory_result.is_duplicate)
        self.assertEqual(record2.inventory_result.duplicate_of, record1.intake_id)

    def test_inventory_classifies_correctly(self):
        """inventory 应正确分类"""
        test_file = os.path.join(self.temp_dir, 'test.pdf')
        with open(test_file, 'w') as f:
            f.write('test')

        record = self.manager.deposit(
            test_file, 'user', DepositMethod.UPLOAD,
            metadata={'source_system': '医学数据库'}
        )
        record = self.manager.inventory(record.intake_id)

        self.assertEqual(record.status, IntakeStatus.REVIEWED)
        self.assertEqual(
            record.classification_result.source_channel,
            SourceChannel.MEDICAL_DATABASE
        )
        self.assertEqual(
            record.classification_result.target_warehouse,
            'raw/external/medical_database/'
        )

    def test_dispatch_moves_file(self):
        """dispatch 应移动文件到目标仓库"""
        test_file = os.path.join(self.temp_dir, 'dispatch_test.pdf')
        with open(test_file, 'w') as f:
            f.write('dispatch test')

        # 完整流程
        record = self.manager.deposit(
            test_file, 'user', DepositMethod.UPLOAD,
            metadata={'source_system': 'V2迁移'}
        )
        record = self.manager.inventory(record.intake_id)
        source = self.manager.dispatch(record.intake_id)

        # 验证文件已移动
        expected_path = os.path.join(self.temp_dir, source.warehouse_path)
        self.assertTrue(os.path.exists(expected_path), f"File should exist at {expected_path}")

        # 验证原文件已不在 inbox
        inbox_path = os.path.join(self.temp_dir, record.inbox_path)
        self.assertFalse(os.path.exists(inbox_path), "File should be moved from inbox")

    def test_full_workflow_minimal(self):
        """最小闭环：deposit -> inventory -> dispatch"""
        test_file = os.path.join(self.temp_dir, 'full_test.pdf')
        with open(test_file, 'w') as f:
            f.write('full workflow test content')

        # 1. Deposit
        record = self.manager.deposit(
            test_file,
            deposited_by='test_user',
            deposit_method=DepositMethod.IMPORT,
            metadata={'source_system': '医学数据库', 'tags': ['test']}
        )
        self.assertEqual(record.status, IntakeStatus.PENDING_REVIEW)

        # 2. Inventory
        record = self.manager.inventory(record.intake_id)
        self.assertEqual(record.status, IntakeStatus.REVIEWED)
        self.assertIsNotNone(record.inventory_result)
        self.assertIsNotNone(record.classification_result)
        self.assertIsNotNone(record.source_key)

        # 3. Dispatch
        source = self.manager.dispatch(record.intake_id)
        self.assertEqual(source.source_channel, SourceChannel.MEDICAL_DATABASE)
        self.assertTrue(source.warehouse_path.startswith('raw/external/medical_database/'))

        # 4. 验证状态已更新
        # 重新加载 registry 检查状态
        self.manager._load_registry()
        for r in self.manager.registry['records']:
            if r['intake_id'] == record.intake_id:
                self.assertEqual(r['status'], 'dispatched')
                break

    def test_registry_persistence(self):
        """注册表应持久化到文件"""
        test_file = os.path.join(self.temp_dir, 'persist_test.pdf')
        with open(test_file, 'w') as f:
            f.write('persist test')

        record = self.manager.deposit(test_file, 'user', DepositMethod.UPLOAD)

        # 创建新的 manager 实例
        new_manager = IntakeManager(self.temp_dir)

        # 验证记录存在
        found = False
        for r in new_manager.registry['records']:
            if r['intake_id'] == record.intake_id:
                found = True
                break
        self.assertTrue(found, "Record should persist in registry")


class TestWarehouseMapping(unittest.TestCase):
    """测试仓库映射完整性"""

    def test_all_channels_have_warehouse(self):
        """所有来源渠道都应有对应仓库"""
        for channel in SourceChannel:
            self.assertIn(channel, SOURCE_CHANNEL_TO_WAREHOUSE,
                         f"Channel {channel} should have warehouse mapping")

    def test_warehouse_paths_are_valid(self):
        """仓库路径应为有效相对路径"""
        for channel, warehouse in SOURCE_CHANNEL_TO_WAREHOUSE.items():
            self.assertTrue(warehouse.startswith('raw/'),
                           f"Warehouse for {channel} should start with 'raw/'")
            self.assertTrue(warehouse.endswith('/'),
                           f"Warehouse for {channel} should end with '/'")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)