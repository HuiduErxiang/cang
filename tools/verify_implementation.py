#!/usr/bin/env python
"""
验证 intake_manager.py 实现
"""

import os
import sys
import tempfile

# 添加 tools 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from intake_manager import (
    DepositMethod,
    IntakeStatus,
    SOURCE_CHANNEL_TO_WAREHOUSE,
    SourceChannel,
    calculate_content_hash,
    classify_by_source_channel,
    generate_intake_id,
    generate_source_key,
    get_file_info,
)


def test_hash_calculation():
    """测试哈希计算"""
    print("Test 1: Hash calculation")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("test content for hash calculation")
        test_file = f.name

    hash_result = calculate_content_hash(test_file)
    print(f"  Hash: {hash_result}")
    print(f"  Length: {len(hash_result)} (expected: 16)")
    assert len(hash_result) == 16, "Hash should be 16 characters"
    os.unlink(test_file)
    print("  PASSED")


def test_id_generation():
    """测试 ID 生成"""
    print("\nTest 2: ID generation")
    intake_id = generate_intake_id("20260316", 1)
    source_key = generate_source_key("20260316", 1)
    print(f"  Intake ID: {intake_id}")
    print(f"  Source key: {source_key}")
    assert intake_id == "INT-20260316-0001", f"Expected INT-20260316-0001, got {intake_id}"
    assert source_key == "SRC-20260316-0001", f"Expected SRC-20260316-0001, got {source_key}"
    print("  PASSED")


def test_classification():
    """测试分类逻辑"""
    print("\nTest 3: Classification (priority arbitration)")

    # Test priority 1: source_system
    r = classify_by_source_channel("医学数据库", None, None, None)
    print(f"  医学数据库 -> {r.target_warehouse} (priority: {r.priority_level})")
    assert r.priority_level == 1, "Should be priority 1"
    assert r.source_channel == SourceChannel.MEDICAL_DATABASE

    r = classify_by_source_channel("V2迁移", None, None, None)
    print(f"  V2迁移 -> {r.target_warehouse} (priority: {r.priority_level})")
    assert r.priority_level == 1
    assert r.source_channel == SourceChannel.V2_HISTORICAL

    # Test priority 2: deposit_method
    r = classify_by_source_channel(None, "upload", None, None)
    print(f"  upload -> {r.target_warehouse} (priority: {r.priority_level})")
    assert r.priority_level == 2
    assert r.source_channel == SourceChannel.USER_UPLOAD

    r = classify_by_source_channel(None, "import", None, None)
    print(f"  import -> {r.target_warehouse} (priority: {r.priority_level})")
    assert r.priority_level == 2
    assert r.source_channel == SourceChannel.BATCH_IMPORT

    # Test priority 3: deposited_by_role
    r = classify_by_source_channel(None, None, "editor", None)
    print(f"  editor -> {r.target_warehouse} (priority: {r.priority_level})")
    assert r.priority_level == 3
    assert r.source_channel == SourceChannel.EDITORIAL

    # Test priority 3: filename match
    r = classify_by_source_channel(None, None, None, "会议纪要.pdf")
    print(f"  会议纪要.pdf -> {r.target_warehouse} (priority: {r.priority_level})")
    assert r.priority_level == 3
    assert r.source_channel == SourceChannel.MEETING_NOTES

    # Test priority 5: orphan
    r = classify_by_source_channel(None, None, None, None)
    print(f"  unknown -> {r.target_warehouse} (priority: {r.priority_level})")
    assert r.priority_level == 5
    assert r.source_channel == SourceChannel.ORPHAN

    print("  PASSED")


def test_priority_override():
    """测试优先级覆盖"""
    print("\nTest 4: Priority override")

    # source_system (priority 1) should override deposit_method (priority 2)
    r = classify_by_source_channel("医学数据库", "upload", None, None)
    print(f"  医学数据库 + upload -> {r.target_warehouse} (priority: {r.priority_level})")
    assert r.priority_level == 1, "source_system should take priority"
    assert r.source_channel == SourceChannel.MEDICAL_DATABASE

    print("  PASSED")


def test_warehouse_mapping():
    """测试仓库映射"""
    print("\nTest 5: Warehouse mapping")
    print(f"  Total channels: {len(SOURCE_CHANNEL_TO_WAREHOUSE)}")
    assert len(SOURCE_CHANNEL_TO_WAREHOUSE) == 12, "Should have 12 channels"

    for channel, warehouse in SOURCE_CHANNEL_TO_WAREHOUSE.items():
        print(f"    {channel.value} -> {warehouse}")

    print("  PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("Intake Manager Implementation Verification")
    print("=" * 60)

    test_hash_calculation()
    test_id_generation()
    test_classification()
    test_priority_override()
    test_warehouse_mapping()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
