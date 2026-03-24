import fitz  # PyMuPDF
import os

pdf_path = "中国去势抵抗性前列腺癌诊治专家共识.pdf"
output_dir = "extracted_images"

os.makedirs(output_dir, exist_ok=True)

doc = fitz.open(pdf_path)
print(f"Total pages: {len(doc)}")

for page_num in range(len(doc)):
    page = doc[page_num]
    
    # Render page to image
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
    img_path = os.path.join(output_dir, f"page_{page_num+1}.png")
    pix.save(img_path)
    print(f"Saved: {img_path}")

doc.close()
print("Done!")
