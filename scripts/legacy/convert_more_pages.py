import fitz
import os

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025 CSCO胃癌指南.pdf'
doc = fitz.open(pdf_path)

# 创建输出目录
output_dir = r'D:\汇度编辑部1\藏经阁\temp_gastric_2025_pages'
os.makedirs(output_dir, exist_ok=True)

# 转换更多关键页面：治疗推荐表格页、更新要点页
key_pages = [76, 77, 78, 79, 22, 23, 24, 25, 64, 65, 115, 116, 117, 182, 183, 184, 185, 192, 193]

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
