import re, sys

with open(r"C:\Users\User\Downloads\formulario-diagnostico-general\index.html", "r", encoding="utf-8") as f:
    html = f.read()

# === 1. Fix PYME area headers: add B., C., D., E., F. ===
html = html.replace('<h2>Mercadeo y Ventas</h2>', '<h2>B. Mercadeo y Ventas</h2>')
html = html.replace('<h2>Operaciones</h2>', '<h2>C. Operaciones</h2>')
html = html.replace('<h2>Finanzas y Contabilidad</h2>', '<h2>D. Finanzas y Contabilidad</h2>')
html = html.replace('<h2>RRHH</h2>', '<h2>E. RRHH</h2>')
html = html.replace('<h2>Direcci\u00f3n Estrat\u00e9gica</h2>', '<h2>F. Direcci\u00f3n Estrat\u00e9gica</h2>')
print("Area headers lettered: OK")

# === 2. Update each PYME area to add process checkboxes before the dropdown ===

# Each area currently has: dropdown -> pasos -> cuello -> mejora
# We need to add: checkboxes for "Que procesos llevan a cabo?" before the dropdown

area_configs = {
    "mv": ("B", [
        "Prospecci\u00f3n de leads",
        "Cotizaci\u00f3n y presupuestos",
        "Cierre de ventas",
        "Postventa y seguimiento",
        "Gesti\u00f3n de CRM",
        "Publicidad y campa\u00f1as",
    ]),
    "ops": ("C", [
        "Gesti\u00f3n de pedidos",
        "Log\u00edstica y entregas",
        "Producci\u00f3n / fabricaci\u00f3n",
        "Control de calidad",
        "Inventario / insumos",
        "Servicio al cliente / soporte",
    ]),
    "fin": ("D", [
        "Facturaci\u00f3n",
        "Conciliaci\u00f3n bancaria",
        "Cierre contable",
        "Gesti\u00f3n de cobranza",
        "Reporting financiero",
    ]),
    "rrhh": ("E", [
        "Selecci\u00f3n y contrataci\u00f3n",
        "N\u00f3mina y beneficios",
        "Evaluaci\u00f3n de desempe\u00f1o",
        "Clima laboral",
        "Capacitaci\u00f3n",
    ]),
    "dir": ("F", [
        "Planeaci\u00f3n anual",
        "Reporting gerencial",
        "Definici\u00f3n de metas / KPIs",
        "An\u00e1lisis de mercado",
        "Gesti\u00f3n presupuestal",
    ]),
}

for key, (letter, processes) in area_configs.items():
    # Build the checkbox HTML for this area
    opts_html = "\n".join([f'      <div class="opcion" data-type="multi" onclick="toggleOpcion(this)">{p}</div>' for p in processes])
    
    checkbox_html = f"""  <div style="margin-bottom:6px;">
    <label>{letter}.1. \u00bfQu\u00e9 procesos de esta \u00e1rea llevan a cabo? <span class="tag">(marca todos los que apliquen)</span></label>
    <div class="opciones" data-multi="{key}-procesos">
{opts_html}
    </div>
  </div>
  <div style="margin-bottom:6px;">
    <label>{letter}.2. Selecciona el proceso principal y/o aquel en el que consideras conveniente aplicar IA</label>
"""
    
    # Find the current first element of this area (the dropdown) and replace its label
    sel_id = f'id="pyme-{key}-proceso"'
    idx = html.find(sel_id)
    if idx == -1:
        print(f"  {key}: sel element not found!")
        continue
    
    # Find the containing div for the dropdown (go back to <div style= before the label)
    # Actually, let's find the label before the select
    label_start = html.rfind('<label', 0, idx)
    label_end = html.find('</label>', idx)
    
    # Extract the existing dropdown HTML (from the select tag to the closing </div>)
    select_start = html.find('<select', label_start)
    div_after_select = html.find('</div>', html.find('</select>', select_start))
    
    dropdown_html = html[label_start:div_after_select+6]
    
    # The old label text
    old_label_pattern = f'<label>{letter}. Selecciona tu proceso principal'
    
    # Build new section with checkboxes + dropdown
    new_section = checkbox_html + f"""    <select id="pyme-{key}-proceso" onchange="autoFillPasos('{key}',this.value)">
      <option value="">Selecciona...</option>
"""
    
    for p in processes:
        p_key = p.lower().split(" / ")[0].split(" (")[0].split("\u00ed")[0].split("\u00f3")[0].split("\u00e1")[0].split("\u00e9")[0].replace(" ", "_").replace("/", "_")
        # Simplify key
        p_key = p.lower().replace(" ", "_").replace("/", "_").replace("\u00ed", "i").replace("\u00f3", "o").replace("\u00e1", "a").replace("\u00e9", "e").replace("\u00fa", "u").replace("\u00f1", "n")[:20]
        new_section += f'      <option value="{p_key}">{p}</option>\n'
    
    new_section += """      <option value="otro">Otro (personalizado)</option>
    </select>
"""
    
    # Replace the old dropdown section with new checkboxes + dropdown
    # Find the exact old text: from the label before select to the end of the dropdown's container div
    # The dropdown div starts with <div style="margin-bottom:6px;"> containing the label+select
    # Let me be more precise
    
    old_dropdown = html[label_start:div_after_select+6]
    # print(f"{key}: old dropdown length = {len(old_dropdown)}")
    
    html = html.replace(old_dropdown, new_section, 1)
    print(f"  {key} ({letter}): restructured OK")

# === 3. Update recolectar function for new checkbox fields ===
# Add collection for the new process checkboxes
for key in area_configs:
    old_line = f"r['{key}_proceso'] = document.getElementById('pyme-{key}-proceso').value;"
    new_lines = f"""r['{key}_procesos_list'] = [...document.querySelectorAll('[data-multi="{key}-procesos"] .active')].map(e => e.textContent.trim()).join(', ');
    r['{key}_proceso'] = document.getElementById('pyme-{key}-proceso').value;"""
    if old_line in html:
        html = html.replace(old_line, new_lines, 1)
        print(f"  {key} recolectar: OK")

# === 4. Update descargar output ===
# Add the processes list to the output for each area
for key in [("mv", "MERCADEO Y VENTAS"), ("ops", "OPERACIONES"), ("fin", "FINANZAS Y CONTABILIDAD"), ("rrhh", "RRHH"), ("dir", "DIRECCI\u00d3N ESTRAT\u00c9GICA")]:
    old = f"txt += 'Proceso: ' + (r.{key[0]}_proceso || '-') + '\\\\n';"
    new = f"txt += 'Procesos que realizan: ' + (r.{key[0]}_procesos_list || '-') + '\\\\n';\n    txt += 'Proceso principal: ' + (r.{key[0]}_proceso || '-') + '\\\\n';"
    if old in html:
        html = html.replace(old, new, 1)
        print(f"  {key[0]} descargar: OK")
    else:
        print(f"  {key[0]} descargar: NOT FOUND")

with open(r"C:\Users\User\Downloads\formulario-diagnostico-general\index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== VERIFICATION ===")
# Check headers
headers = re.findall(r'<h2>([^<]*)</h2>', html)
print("Headers:")
for h in headers:
    if any(x in h for x in ['0.', 'A.', 'B.', 'C.', 'D.', 'E.', 'F.', 'G.', 'Tecnolog', 'Micro', 'Procesos', 'madurez']):
        print(f"  {h}")

# Check all new checkbox groups exist
for key in area_configs:
    if f'data-multi="{key}-procesos"' in html:
        print(f"  Checkbox {key}: OK")
    else:
        print(f"  Checkbox {key}: NOT FOUND")

# Check numbered labels
for key, (letter, _) in area_configs.items():
    if f'{letter}.1.' in html:
        print(f"  {letter}.1 sub-label: OK")
    else:
        print(f"  {letter}.1 sub-label: NOT FOUND")

print(f"Divs: {html.count('<div')} / {html.count('</div>')} diff={html.count('<div')-html.count('</div>')}")
