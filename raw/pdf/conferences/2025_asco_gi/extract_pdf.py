import fitz
import json
import re

pdf_path = '2025 ASCO GI摘要集/2025 ASCO GI-摘要集-食管癌和胃癌.pdf'
doc = fitz.open(pdf_path)

# Get basic info
total_pages = len(doc)

# Extract text from all pages
full_text = ''
for i, page in enumerate(doc):
    text = page.get_text()
    full_text += text + '\n'

# Extract abstracts - look for abstract number pattern followed by session type and title
abstracts = []

# Better approach - split by abstract markers
sections = re.split(r'\n(?=(?:LBA)?\d{3,}\s*\n(?:Rapid Oral |Oral |Poster |Poster Discussion )?Abstract Session)', full_text)

abstract_titles = []
for section in sections[1:]:  # Skip first empty section
    lines = section.strip().split('\n')
    if len(lines) >= 2:
        abs_num = lines[0].strip()
        session_type = ''
        title_start = 1
        if 'Session' in lines[1]:
            session_type = lines[1].strip()
            title_start = 2
        
        # Collect title lines
        title_lines = []
        for i in range(title_start, min(title_start + 6, len(lines))):
            line = lines[i].strip()
            if line and not line.startswith(('Background:', 'Methods:', 'Results:', 'Conclusions:', 'ESOPHAGEAL')):
                if ';' in line and len(title_lines) > 0:
                    break
                title_lines.append(line)
            elif line.startswith(('Background:', 'Methods:', 'Conclusions:', 'ESOPHAGEAL')):
                break
        
        if title_lines:
            title = ' '.join(title_lines)
            if len(title) > 20:
                abstract_titles.append({'id': abs_num, 'type': session_type, 'title': title[:250]})

# Get key findings from conclusions
conclusions = re.findall(r'Conclusions?: ([^\n]+(?:\n[^\n]+){0,3})', full_text, re.MULTILINE)
key_findings = []
for c in conclusions:
    c_clean = c.strip().replace('\n', ' ')
    if len(c_clean) > 30:
        key_findings.append(c_clean[:300])

# Remove duplicates
key_findings = list(set(key_findings))

# Look for tables - table-like content
tables = []
table_keywords = ['Table', 'Safety', 'OR', 'HR', 'p-value', 'n (%)']
for keyword in table_keywords:
    if keyword in full_text:
        # Find context around table keywords
        table_contexts = re.findall(r'(?:Table \d+|Safety)[^\n]*(?:\n[^\n]+){3,15}', full_text)
        for ctx in table_contexts[:5]:
            tables.append(ctx[:200].replace('\n', ' '))

tables = list(set(tables))

# Look for figures
figures = []
figure_matches = re.findall(r'(Figure \d+[^\n]*)', full_text)
figures = list(set([f[:100] for f in figure_matches]))

print(f'Total pages: {total_pages}')
print(f'Found {len(abstract_titles)} abstracts')
print(f'Found {len(key_findings)} key findings')
print(f'Found {len(tables)} tables')
print(f'Found {len(figures)} figures')

# Save to JSON
output = {
    'document_type': 'conference',
    'title': '2025 ASCO GI - 食管癌和胃癌摘要集',
    'conference_name': 'ASCO GI',
    'year': 2025,
    'language': 'Chinese/English',
    'total_pages': total_pages,
    'disease_area': 'Esophageal and Gastric Cancer',
    'abstract_count': len(abstract_titles),
    'abstracts': abstract_titles,
    'key_findings': key_findings[:15],
    'tables': tables[:10],
    'figures': figures[:10],
    'key_conclusions': key_findings[:10]
}

print('\n=== JSON OUTPUT ===')
print(json.dumps(output, ensure_ascii=False, indent=2))
