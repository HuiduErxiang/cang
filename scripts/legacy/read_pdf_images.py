import fitz
import os

doc = fitz.open(r'raw\pdf\conferences\2025_asco_gi\2025 ASCO GI 会议幻灯集锦（中文版）-恒瑞医学\2025 ASCO GI 胰腺癌领域研究进展-恒瑞医学.pdf')

# 创建输出目录
output_dir = 'temp_pancreatic_pages'
os.makedirs(output_dir, exist_ok=True)

print(f"Total pages: {len(doc)}")

# 将剩余页面转换为图片以检查内容 (61-86页)
for i in range(60, len(doc)):
    page = doc[i]
    # 提高分辨率
    mat = fitz.Matrix(2, 2)
    pix = page.get_pixmap(matrix=mat)
    output_path = f"{output_dir}/page_{i+1}.png"
    pix.save(output_path)
    print(f"Saved page {i+1} to {output_path}")

print("Done converting pages 61-86!")
