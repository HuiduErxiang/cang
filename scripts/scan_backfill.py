#!/usr/bin/env python3
"""快速扫描蒸馏样本，按产品线分组，输出回填优先级清单数据"""
import json, os, sys

samples_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'distillation_samples')
rebuilt_dir = os.path.join(os.path.dirname(__file__), '..', 'publish', 'current', 'consumers', 'xiakedao', 'staging', 'evidence', 'rebuilt')

# 扫描 rebuilt 里已有的 evidence_v2
existing_ev2 = {}
for f in os.listdir(rebuilt_dir):
    if f.endswith('_evidence_v2.json'):
        pid = f.replace('_evidence_v2.json', '')
        try:
            d = json.load(open(os.path.join(rebuilt_dir, f), 'r', encoding='utf-8'))
            has_bt = any('boundary_tags' in s.get('metadata', {}) for s in d.get('v2_sources', []))
            existing_ev2[pid] = {'facts': len(d.get('v2_facts', [])), 'has_bt': has_bt}
        except:
            existing_ev2[pid] = {'facts': 0, 'has_bt': False}

print("=== 已有 evidence_v2 文件 ===")
for pid, info in sorted(existing_ev2.items()):
    bt_str = "✅ has_bt" if info['has_bt'] else "⬜ no_bt"
    print(f"  {pid:50s} facts={info['facts']:3d}  {bt_str}")

# 扫描蒸馏样本
ad_keywords = ['lecanemab', 'clarity', '仑卡奈', 'alzheimer', 'trailblazer', 'donanemab', '阿尔茨海默', '认知', 'lemborexant', '莱博雷生']
gastric_keywords = ['gastric', '胃癌', 'keynote-811', 'keynote-062', 'rainbow', 'spotlight', 'orient', 'toga', 'avagast', 'her2', 'checkmate649', 'checkmate 649', 'rationale', 'glow', 'claudin', 'dg-0', 'compassion']

ad_files = []
gastric_files = []
other_files = []

for f in sorted(os.listdir(samples_dir)):
    if not f.endswith('.json'):
        continue
    fl = f.lower()
    if any(k in fl for k in ad_keywords):
        ad_files.append(f)
    elif any(k in fl for k in gastric_keywords):
        gastric_files.append(f)
    else:
        other_files.append(f)

print(f"\n=== 蒸馏样本分组 ===")
print(f"  AD/神经: {len(ad_files)} 篇")
for x in ad_files:
    print(f"    {x}")
print(f"\n  胃癌产品线: {len(gastric_files)} 篇")
for x in gastric_files:
    print(f"    {x}")
print(f"\n  其他: {len(other_files)} 篇 (前10)")
for x in other_files[:10]:
    print(f"    {x}")
if len(other_files) > 10:
    print(f"    ... and {len(other_files)-10} more")

print(f"\n=== 总计 ===")
print(f"  蒸馏样本总数: {len(ad_files) + len(gastric_files) + len(other_files)}")
print(f"  evidence_v2 总数: {len(existing_ev2)}")
print(f"  已有 boundary_tags 的 evidence_v2: {sum(1 for v in existing_ev2.values() if v['has_bt'])}")
