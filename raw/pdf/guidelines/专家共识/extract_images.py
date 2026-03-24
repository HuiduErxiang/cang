import fitz
import os

# Open the PDF file
pdf_path = "胃癌HER2检测指南(2016版).pdf"
doc = fitz.open(pdf_path)

# Create output directory
output_dir = "pdf_images"
os.makedirs(output_dir, exist_ok=True)

# Render each page to image
for i, page in enumerate(doc):
    # Render at 2x zoom for better quality
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    output_path = f"{output_dir}/page_{i+1}.png"
    pix.save(output_path)
    print(f"Saved: {output_path}")

print(f"\nTotal pages rendered: {len(doc)}")
