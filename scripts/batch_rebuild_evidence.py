#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量重建第 1、2 批有 boundary_tags 的文献，输出 evidence_v2 到 rebuilt 目录"""

import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
try:
    from scripts.rebuild_evidence_v2 import load_distillation, build_evidence_v2, PUBLISH_DIR
except ImportError:
    print("Failed to import rebuild_evidence_v2 utilities")
    sys.exit(1)

SAMPLES_DIR = BASE_DIR / "output" / "distillation_samples"

AD_KEYWORDS = ['lecanemab', 'clarity', '仑卡奈', 'alzheimer', 'trailblazer', 'donanemab', '阿尔茨海默', 'lemborexant', '莱博雷生']
GASTRIC_KEYWORDS = ['gastric', '胃癌', 'keynote-811', 'keynote-062', 'rainbow', 'spotlight', 'orient', 'toga', 'avagast', 'her2', 'checkmate649', 'checkmate 649', 'rationale', 'glow', 'claudin', 'dg-0', 'compassion']

def is_target(fl):
    fl = fl.lower()
    return any(k in fl for k in AD_KEYWORDS + GASTRIC_KEYWORDS)

def main():
    PUBLISH_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    success = 0
    for f in os.listdir(SAMPLES_DIR):
        if not f.endswith('.json'):
            continue
        if is_target(f):
            count += 1
            path = SAMPLES_DIR / f
            distill = load_distillation(str(path))
            
            # Skip if boundary_tags missing (though they should all have it now)
            if "boundary_tags" not in distill:
                print(f"Skipping {f} - missing boundary tags")
                continue
                
            # Product ID inference
            short_name = distill.get("doc_id", "unknown").split('_')[1] if "_" in distill.get("doc_id", "") else f.replace('.json', '')
            # Handle empty product ID safely
            if not short_name:
                short_name = f.replace('.json', '')
            
            try:
                evidence = build_evidence_v2(distill, short_name)
                output_path = PUBLISH_DIR / f"{short_name}_evidence_v2.json"
                
                with open(output_path, "w", encoding="utf-8") as out:
                    json.dump(evidence, out, ensure_ascii=False, indent=2)
                success += 1
            except Exception as e:
                print(f"Failed to rebuild {f}: {e}")
                
    print(f"\nRebuild completed. Target: {count}, Success: {success}")
    
    # Check completeness
    rebuilt_count = sum(1 for f in os.listdir(PUBLISH_DIR) if f.endswith('.json'))
    print(f"Evidence files in staging/evidence/rebuilt: {rebuilt_count}")

if __name__ == "__main__":
    main()
