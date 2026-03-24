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

# Better pattern to match abstracts
# Look for lines that are just numbers (abstract IDs)
lines = full_text.split('\n')

abstracts = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    # Match abstract number (digits only or LBA + digits)
    if re.match(r'^(\d{3,}|LBA\d{3,})$', line):
        abs_id = line
        i += 1
        session_type = ''
        # Check if next line is session type
        if i < len(lines) and 'Session' in lines[i]:
            session_type = lines[i].strip()
            i += 1
        
        # Collect title lines until we hit authors or background
        title_lines = []
        while i < len(lines):
            current = lines[i].strip()
            # Stop conditions
            if current.startswith(('Background:', 'Methods:', 'Results:', 'Conclusions:', 'ESOPHAGEAL')):
                break
            if ';' in current and len(title_lines) > 0:  # Authors line
                # Check if it looks like author line (contains semicolon and likely affiliation)
                if any(x in current.lower() for x in ['hospital', 'university', 'center', 'institute', 'china', 'japan', 'korea', 'usa', 'germany']):
                    break
            if re.match(r'^(\d{3,}|LBA\d{3,})$', current):  # Next abstract
                break
            if current:
                title_lines.append(current)
            i += 1
            if len(title_lines) > 8:
                break
        
        if title_lines:
            title = ' '.join(title_lines)
            # Clean up title - remove author info if it got included
            if ';' in title:
                title = title.split(';')[0]
            if len(title) > 25:
                abstracts.append({
                    'id': abs_id,
                    'type': session_type,
                    'title': title[:280]
                })
    else:
        i += 1

# Get unique conclusions
conclusions = re.findall(r'Conclusions?:\s*([^\n]+(?:\n(?![A-Z][a-z]+ \d|Background|Methods|Table|Figure)[^\n]+){0,4})', full_text, re.MULTILINE | re.IGNORECASE)
key_findings = []
for c in conclusions:
    c_clean = c.strip().replace('\n', ' ')
    # Remove trailing keywords
    for kw in ['Research Sponsor:', 'Clinical trial information:', 'ESOPHAGEAL']:
        if kw in c_clean:
            c_clean = c_clean.split(kw)[0]
    c_clean = c_clean.strip()
    if len(c_clean) > 30 and len(c_clean) < 500:
        key_findings.append(c_clean)

# Remove duplicates while preserving order
seen = set()
unique_findings = []
for f in key_findings:
    if f not in seen:
        seen.add(f)
        unique_findings.append(f)

print(f'Total pages: {total_pages}')
print(f'Found {len(abstracts)} abstracts')

# Save to JSON
output = {
    'document_type': 'conference',
    'title': '2025 ASCO GI - 食管癌和胃癌摘要集',
    'conference_name': 'ASCO GI',
    'year': 2025,
    'language': 'Chinese/English',
    'total_pages': total_pages,
    'disease_area': 'Esophageal and Gastric Cancer',
    'abstract_count': len(abstracts),
    'abstracts': [{'number': a['id'], 'session_type': a['type'], 'title': a['title']} for a in abstracts],
    'key_findings': unique_findings[:20],
    'tables': [],
    'figures': [],
    'key_conclusions': unique_findings[:10]
}

print('\n=== JSON OUTPUT ===')
print(json.dumps(output, ensure_ascii=False, indent=2))
