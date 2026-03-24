import fitz

pdf_path = r'D:\汇度编辑部1\藏经阁\raw\pdf\guidelines\2025 CSCO指南\2025 CSCO胃癌指南.pdf'
doc = fitz.open(pdf_path)

with open('pdf_image_check.txt', 'w', encoding='utf-8') as f:
    # 检查前10页的内容类型
    for page_num in range(10):
        page = doc[page_num]
        text = page.get_text()
        images = page.get_images()
        
        f.write(f"\n=== Page {page_num + 1} ===\n")
        f.write(f"Text length: {len(text)}\n")
        f.write(f"Number of images: {len(images)}\n")
        f.write(f"Text preview: {repr(text[:500])}\n")

print("Output saved to pdf_image_check.txt")
doc.close()
