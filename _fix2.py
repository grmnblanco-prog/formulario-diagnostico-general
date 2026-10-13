import re

with open(r"C:\Users\User\Downloads\formulario-diagnostico-general\index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Fix infrastructure text
html = html.replace(
    'Equipos de c\u00f3mputo con prestaciones para IA local (m\u00e1s de 16 GB RAM, procesador moderno, disco SSD, ojal\u00e1 con tarjeta gr\u00e1fica)',
    'Equipos con prestaciones para IA local (16 GB+ RAM, SSD, ojal\u00e1 con GPU)'
)

# 2. Strip ALL existing prefixes from ALL labels first
# Find all labels and remove prefixes like "B.1. ", "1. ", "G.1. ", "5. " etc
html = re.sub(r'<label>(?:[A-Z]\.\d+\.\s+)?(?:\d+\.\s+)?', '<label>', html)

# 3. Now renumber section A labels (should be first 4 <label> in data-section="basica")
basica_idx = html.find('data-section="basica"')
basica_end = html.find('data-section="micro"')
if basica_end == -1:
    basica_end = html.find('data-section="pyme"')

basica_html = html[basica_idx:basica_end]
# Number labels in section A
counter = 1
def renumb_a(m):
    global counter
    c = counter
    counter += 1
    return f'<label>{c}. '  # Keep the text after 
basica_html = re.sub(r'<label>(?![\d]+\.)', renumb_a, basica_html)
html = html[:basica_idx] + basica_html + html[basica_end:]
a_count = counter - 1
print(f"Section A: {a_count} labels numbered 1-{a_count}")

# 4. Number Micro section B labels (continue from a_count + 1)
micro_idx = html.find('data-section="micro"')
if micro_idx > -1:
    micro_start = html.find('>', micro_idx) + 1
    # Find where micro card ends (next data-section or next div)
    micro_end = html.find('data-section="pyme"', micro_idx)
    micro_html = html[micro_start:micro_end]
    def renumb_micro(m):
        global counter
        c = counter
        counter += 1
        return f'<label>{c}. '
    micro_html = re.sub(r'<label>', renumb_micro, micro_html)
    html = html[:micro_start] + micro_html + html[micro_end:]
    micro_count = counter - 1 - a_count
    print(f"Micro B: {micro_count} labels numbered {a_count+1}-{counter-1}")

# 5. Number PYME area labels (B-F) - continue counting
pyme_start = html.find('data-section="pyme"')
pyme_end = html.find('</div>\n</div>\n\n', pyme_start) + len('</div>\n</div>\n\n')
pyme_html = html[pyme_start:pyme_end]

def renumb_pyme(m):
    global counter
    # Get the full match, extract the label tag
    full = m.group(0)
    c = counter
    counter += 1
    # Return the label tag with number, keeping the original text
    return f'<label>{c}. '

pyme_html = re.sub(r'<label>(?!\d)', renumb_pyme, pyme_html)
# Limit replacement to prevent over-counting
# Actually let me count the actual labels first
label_count = pyme_html.count('<label>') - 1  # subtract 1 for the first extra match
# Better approach: find all labels that DON'T already start with a number
pyme_labels = list(re.finditer(r'<label>(?!\d)([^<]+)', pyme_html))
print(f"PYME labels found: {len(pyme_labels)}")

for m in pyme_labels:
    c = counter
    counter += 1
    old = m.group(0)
    new = f'<label>{c}. '  # Keep text as is
    pyme_html = pyme_html.replace(old, new, 1)

html = html[:pyme_start] + pyme_html + html[pyme_end:]

# 6. Number G section labels
g_idx = html.find('G. Tecnolog')
g_start = html.rfind('<div class="card hidden"', 0, g_idx)
g_end = html.find('</div>\n</div>\n\n', g_idx)
if g_end == -1:
    g_end = html.find('NIVEL DE MADUREZ', g_idx)

g_html = html[g_start:g_end]
g_labels = list(re.finditer(r'<label>(?!\d)([^<]+)', g_html))
print(f"G labels found: {len(g_labels)}")

for m in g_labels:
    c = counter
    counter += 1
    old = m.group(0)
    new = f'<label>{c}. '
    g_html = g_html.replace(old, new, 1)

html = html[:g_start] + g_html + html[g_end:]

# 7. Clean up any remaining unnumbered labels
# Check for labels that don't start with a number
remaining = re.findall(r'<label>(?!\d+\.\s)([^<]{5,80})</label>', html)
if remaining:
    print(f"Unnumbered labels remaining: {len(remaining)}")
    for r in remaining[:5]:
        print(f"  {r}")

# 8. Remove double numbers like "5. 4. " or "5. ¿"  
html = re.sub(r'<label>(\d+)\.\s+(\d+)\.\s', r'<label>\1. ', html)

# Verify final labels  
all_labels = re.findall(r'<label>(\d+\.\s[^<]{3,80})</label>', html)
print(f"\nTotal numbered labels: {len(all_labels)}")
# Group by number
seen = {}
for l in all_labels:
    num = l.split('.')[0]
    if num.isdigit():
        if num not in seen:
            seen[num] = []
        seen[num].append(l)
        
for num in sorted(seen.keys(), key=int):
    items = seen[num]
    if len(items) == 1:
        print(f"  {items[0]}")
    else:
        print(f"  {num}: {len(items)} labels - {items[0][:40]}...")

print(f"\nDivs: {html.count('<div')} / {html.count('</div>')}")

with open(r"C:\Users\User\Downloads\formulario-diagnostico-general\index.html", "w", encoding="utf-8") as f:
    f.write(html)
