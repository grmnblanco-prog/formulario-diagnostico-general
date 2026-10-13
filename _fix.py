import re

with open(r"C:\Users\User\Downloads\formulario-diagnostico-general\index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove "0." prefix
html = html.replace('<h2>0. Datos de la empresa</h2>', '<h2>Datos de la empresa</h2>')

# 2. Fix autoFillPasos dropdown values - replace truncated keys with short ones
value_fixes = [
    ("logistica_y_entregas", "logistica"),
    ("produccion___fabrica", "produccion"), 
    ("inventario___insumos", "inventario"),
    ("servicio_al_cliente_", "soporte"),
    ("conciliacion_bancari", "conciliacion"),
    ("gestion_de_cobranza", "cobranza"),
    ("reporting_financiero", "reporting"),
    ("seleccion_y_contrata", "seleccion"),
    ("nomina_y_beneficios", "nomina"),
    ("evaluacion_de_desemp", "evaluacion"),
    ("reporting_gerencial", "reporting_g"),
    ("definicion_de_metas_", "metas"),
    ("analisis_de_mercado", "mercado"),
    ("gestion_presupuestal", "presupuesto"),
]
for old_val, new_val in value_fixes:
    html = html.replace(f'value="{old_val}"', f'value="{new_val}"')

# 3. Add reporting_g to stepsMap
html = html.replace(
    '"reporting":',
    '"reporting_g": "Recopila datos \\u2192 Analiza \\u2192 Prepara informe \\u2192 Presenta \\u2192 Decide",\n    "reporting":'
)

# 4. Number all labels within each PYME area (B, C, D, E, F)
for letter in ["B", "C", "D", "E", "F"]:
    hdr = f'<h2>{letter}. '
    idx_hdr = html.find(hdr)
    if idx_hdr == -1:
        continue
    # Find the end of this area (next h2 with letter or G)
    next_letters = [l for l in ["C", "D", "E", "F", "G", "Tecnolog"] if l > letter or (letter == "F" and l == "Tecnolog")]
    end_idx = len(html)
    for nl in next_letters:
        ni = html.find(f'<h2>{nl}', idx_hdr + 10)
        if ni > -1 and ni < end_idx:
            end_idx = ni
    area_html = html[idx_hdr:end_idx]
    
    # Find all <label> tags that aren't already numbered
    count = 0
    for m in re.finditer(r'<label>([^<]*)</label>', area_html):
        txt = m.group(1)
        if re.match(r'^[A-Z]\.\d+\.\s', txt):
            continue  # skip already numbered
        count += 1
        old = m.group(0)
        new = f'<label>{letter}.{count}. {txt}</label>'
        area_html = area_html.replace(old, new, 1)
    
    html = html[:idx_hdr] + area_html + html[end_idx:]
    print(f"  {letter}: {count} labels numbered")

# 5. Number G section labels (Tecnología y equipo)
idx_g = html.find('<h2>G. Tecnolog')
# Find the end - next h2 or </form>
rest = html[idx_g+20:]
end_g = idx_g + 20 + rest.find('</div>\n</div>\n\n')
if end_g - idx_g < 20:
    end_g = html.find('</form>', idx_g)
g_html = html[idx_g:end_g]

g_count = 0
for m in re.finditer(r'<label>([^<]*)</label>', g_html):
    txt = m.group(1)
    if re.match(r'^[A-Z]\.\d+\.\s', txt):
        continue
    g_count += 1
    old = m.group(0)
    new = f'<label>G.{g_count}. {txt}</label>'
    g_html = g_html.replace(old, new, 1)

html = html[:idx_g] + g_html + html[end_g:]
print(f"  G: {g_count} labels numbered")

with open(r"C:\Users\User\Downloads\formulario-diagnostico-general\index.html", "w", encoding="utf-8") as f:
    f.write(html)

# Verify
import re
print("\n=== Verification ===")
print(f"'0. Datos': {'0. Datos' in html}")

# Check all labels
labels = re.findall(r'<label>([A-Z]\.[\d]+\.[^<]+)</label>', html)
print(f"\nNumbered labels ({len(labels)}):")
for l in sorted(set(labels)):
    print(f"  {l}")

# Check dropdown values match stepsMap
idx_sm = html.find("stepsMap = {")
end_sm = html.find("};", idx_sm)
step_keys = set(re.findall(r'"(\w+)"\s*:', html[idx_sm:end_sm]))
print(f"\nstepsMap keys ({len(step_keys)}): {sorted(step_keys)}")

# Check all option values are in stepsMap
all_vals = set(re.findall(r'<option value="(\w+)"', html))
option_vals = {v for v in all_vals if v not in ('', 'otro')}
missing = option_vals - step_keys
if missing:
    print(f"MISSING from stepsMap: {missing}")
else:
    print(f"All {len(option_vals)} option values match stepsMap: OK")

print(f"\nDivs: {html.count('<div')} / {html.count('</div>')}")
