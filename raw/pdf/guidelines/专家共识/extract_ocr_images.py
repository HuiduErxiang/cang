import pytesseract
from PIL import Image
import os

pdf_name = "中国去势抵抗性前列腺癌诊治专家共识.pdf"
base_name = os.path.splitext(pdf_name)[0]
image_dir = "pdf_images"

print(f"Extracting text from images for: {pdf_name}")
print("=" * 60)

all_text = []
for i in range(1, 10):  # Check up to 10 pages
    img_path = os.path.join(image_dir, f"page_{i}.png")
    if not os.path.exists(img_path):
        break
    
    print(f"\n--- Page {i} ---")
    try:
        image = Image.open(img_path)
        # Use Chinese language for OCR
        text = pytesseract.image_to_string(image, lang='chi_sim')
        print(text[:2000])
        all_text.append(f"--- Page {i} ---\n{text}")
    except Exception as e:
        print(f"Error: {e}")

# Save to file
output_file = f"{base_name}_extracted.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(all_text))
print(f"\n\nSaved to: {output_file}")
