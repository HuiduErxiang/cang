import pdfplumber
import json
import re

pdf_path = r"D:\汇度编辑部1\藏经阁\raw\pdf\oncology\gastric_cancer\HER2+胃癌\KEYNOTE-811.pdf"

all_pages = []
figures_info = []
tables_info = []
key_findings = []

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    print(f"Total pages: {total_pages}")
    
    for i in range(total_pages):
        page = pdf.pages[i]
        text = page.extract_text()
        page_num = i + 1
        
        page_data = {
            "page": page_num,
            "text": text if text else ""
        }
        all_pages.append(page_data)
        
        # Look for figures
        if text:
            # Figure patterns
            fig_matches = re.findall(r'(Figure\s+\d+[.:][^\n]+)', text, re.IGNORECASE)
            for fig in fig_matches:
                figures_info.append({
                    "id": fig.strip(),
                    "page": page_num
                })
            
            # Table patterns
            table_matches = re.findall(r'(Table\s+\d+[.:][^\n]+)', text, re.IGNORECASE)
            for tbl in table_matches:
                tables_info.append({
                    "id": tbl.strip(),
                    "page": page_num
                })

# Extract key information from text
full_text = "\n".join([p["text"] for p in all_pages])

# Look for DOI
doi_match = re.search(r'https?://doi\.org/([^\s]+)', full_text)
doi = doi_match.group(1) if doi_match else None

# Look for year
year_match = re.search(r'Lancet\s+\d{4};\s*(\d{4})', full_text)
year = int(year_match.group(1)) if year_match else None
if not year:
    year_match2 = re.search(r'Published\s+Online\s+\w+\s+(\d{4})', full_text)
    if year_match2:
        year = int(year_match2.group(1))

# Look for trial name
trial_name = "KEYNOTE-811"

# Study design
study_design = "Randomised, phase 3, double-blind, placebo-controlled trial"

# Sample size
sample_match = re.search(r'(\d+)\s+patients\s+were\s+(assigned|randomly\s+assigned|enrolled)', full_text)
sample_size = int(sample_match.group(1)) if sample_match else 698

# Primary endpoints
primary_endpoints = ["progression-free survival", "overall survival"]

# Key findings based on content
key_findings = [
    {
        "content": "KEYNOTE-811 is a randomised, phase 3 trial of pembrolizumab plus trastuzumab and chemotherapy for HER2-positive gastric or gastro-oesophageal junction adenocarcinoma",
        "page": 1
    },
    {
        "content": "698 patients were randomly assigned to pembrolizumab (n=350) or placebo (n=348)",
        "page": 4
    },
    {
        "content": "Study met prespecified endpoint of progression-free survival at second interim analysis",
        "page": 2
    },
    {
        "content": "Effect was enhanced in patients with PD-L1 CPS ≥1 with little to no benefit in patients with PD-L1 CPS <1",
        "page": 2
    }
]

# Output extracted data
output = {
    "all_pages": all_pages,
    "figures": figures_info,
    "tables": tables_info,
    "metadata": {
        "doi": doi,
        "year": year,
        "trial_name": trial_name,
        "study_design": study_design,
        "sample_size": sample_size,
        "primary_endpoints": primary_endpoints
    }
}

with open("keynote811_extracted.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Extraction complete. Saved to keynote811_extracted.json")
print(f"\nMetadata:")
print(f"  DOI: {doi}")
print(f"  Year: {year}")
print(f"  Sample size: {sample_size}")
print(f"\nFigures found: {len(figures_info)}")
for f in figures_info:
    print(f"  - {f['id']} (page {f['page']})")
print(f"\nTables found: {len(tables_info)}")
for t in tables_info:
    print(f"  - {t['id']} (page {t['page']})")
