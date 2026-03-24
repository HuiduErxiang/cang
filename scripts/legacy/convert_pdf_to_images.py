import fitz
import os

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025 CSCO胃癌指南.pdf'
doc = fitz.open(pdf_path)

# 创建输出目录
output_dir = r'D:\汇度编辑部1\藏经阁\temp_gastric_2025_pages'
os.makedirs(output_dir, exist_ok=True)

# 转换关键页面：封面、前言、目录、推荐等级定义页、以及各章节页
key_pages = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100]

converted = []
for page_num in key_pages:
    if page_num <= len(doc):
        page = doc[page_num - 1]
        # 提高分辨率
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)
        output_path = os.path.join(output_dir, f'page_{page_num:03d}.png')
        pix.save(output_path)
        converted.append(page_num)

doc.close()
print(f"Converted pages: {converted}")
