import json
import sys
import re
import fitz

doc = fitz.open(r'raw\pdf\guidelines\2024 CSCO指南\2024CSCO免疫检查点抑制剂临床应用指南.pdf')

# 提取目录页和前25页的完整文本
all_text = []
for page_num in range(min(25, len(doc))):
    page = doc[page_num]
    text = page.get_text()
    all_text.append({'page': page_num + 1, 'text': text})

# 保存文本以便分析
with open('temp_extracted_text.json', 'w', encoding='utf-8') as f:
    json.dump(all_text, f, ensure_ascii=False, indent=2)

print(f'Extracted {len(all_text)} pages')

# 提取关键页面内容
for item in all_text[:5]:
    print(f"=== Page {item['page']} ===")
    print(item['text'][:500])
    print('...')
