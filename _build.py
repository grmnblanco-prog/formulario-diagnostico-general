import re, sys

with open(r"C:\Users\User\Downloads\formulario-diagnostico-general\index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. CSS indicators
old_css = ".opcion {\n    display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 8px;\n    border: 1px solid rgba(45,42,36,.08); cursor: pointer; font-size: 12px; background: #fff; transition: .15s;\n    max-width: 100%; word-break: break-word;\n  }"
new_css = """.opcion {
    display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 8px;
    border: 1px solid rgba(45,42,36,.08); cursor: pointer; font-size: 12px; background: #fff; transition: .15s;
    max-width: 100%; word-break: break-word;
  }
  .opcion[data-type="radio"]::before { content: "\u25cb"; font-size: 14px; margin-right: 4px; }
  .opcion[data-type="multi"]::before { content: "\u25a1"; font-size: 14px; margin-right: 4px; }
  .opcion[data-type="radio"].active::before { content: "\u25cf"; color: #E8633A; }
  .opcion[data-type="multi"].active::before { content: "\u2611"; color: #E8633A; }"""
if old_css in html:
    html = html.replace(old_css, new_css)
    print("CSS: OK")
else:
    print("CSS: NOT FOUND")
    sys.exit(1)

# 2. Add data-type attributes
html = html.replace('class="opcion" onclick="toggleOpcion(this)"', 'class="opcion" data-type="multi" onclick="toggleOpcion(this)"')
html = html.replace('class="opcion" onclick="toggleRadio(this,', 'class="opcion" data-type="radio" onclick="toggleRadio(this,')
html = html.replace('class="madurez-card" onclick="selectMadurez(this)"', 'class="madurez-card" data-type="radio" onclick="selectMadurez(this)"')
print("data-type attributes: OK")

# 3. Build new PYME section with dropdowns
area_opts = {
    "mv": ("Mercadeo y Ventas", "4", [
        ("", "Selecciona..."),
        ("prospeccion", "Prospecci\u00f3n de leads"),
        ("cotizacion", "Cotizaci\u00f3n y presupuestos"),
        ("cierre", "Cierre de ventas"),
        ("postventa", "Postventa y seguimiento"),
        ("crm", "Gesti\u00f3n de CRM"),
        ("publicidad", "Publicidad y campa\u00f1as"),
        ("otro", "Otro (personalizado)"),
    ], {
        "prospeccion": "Lead entra \u2192 Se califica \u2192 Se asigna \u2192 Se contacta",
        "cotizacion": "Solicitud \u2192 Calcula precio \u2192 Env\u00eda propuesta \u2192 Negocia \u2192 Cierra",
        "cierre": "Propuesta aceptada \u2192 Contrato \u2192 Pago inicial \u2192 Ejecuta",
        "postventa": "Cliente recibe \u2192 Encuesta \u2192 Soporte \u2192 Fidelizaci\u00f3n",
        "crm": "Contacto \u2192 Registro \u2192 Segmenta \u2192 Campa\u00f1a \u2192 Reporta",
        "publicidad": "Brief \u2192 Crea contenido \u2192 Publica \u2192 Mide \u2192 Optimiza",
        "otro": "",
    }),
    "ops": ("Operaciones", "5", [
        ("", "Selecciona..."),
        ("pedidos", "Gesti\u00f3n de pedidos"),
        ("logistica", "Log\u00edstica y entregas"),
        ("produccion", "Producci\u00f3n / fabricaci\u00f3n"),
        ("calidad", "Control de calidad"),
        ("inventario", "Inventario / insumos"),
        ("soporte", "Servicio al cliente / soporte"),
        ("otro", "Otro (personalizado)"),
    ], {
        "pedidos": "Pedido entra \u2192 Verifica stock \u2192 Prepara \u2192 Despacha \u2192 Confirma",
        "logistica": "Solicitud de env\u00edo \u2192 Alista \u2192 Ruta \u2192 Entrega \u2192 Confirma",
        "produccion": "Insumos \u2192 Proceso \u2192 Control calidad \u2192 Empaque \u2192 Almacena",
        "calidad": "Muestra \u2192 Inspecciona \u2192 Mide \u2192 Reporta \u2192 Aprueba/Rechaza",
        "inventario": "Recepci\u00f3n \u2192 Registra \u2192 Almacena \u2192 Actualiza \u2192 Reporta",
        "soporte": "Ticket abre \u2192 Clasifica \u2192 Resuelve \u2192 Cierra \u2192 Encuesta",
        "otro": "",
    }),
    "fin": ("Finanzas y Contabilidad", "6", [
        ("", "Selecciona..."),
        ("facturacion", "Facturaci\u00f3n"),
        ("conciliacion", "Conciliaci\u00f3n bancaria"),
        ("cierre", "Cierre contable"),
        ("cobranza", "Gesti\u00f3n de cobranza"),
        ("reporting", "Reporting financiero"),
        ("otro", "Otro (personalizado)"),
    ], {
        "facturacion": "Venta \u2192 Genera factura \u2192 Env\u00eda \u2192 Registra \u2192 Archiva",
        "conciliacion": "Exporta movimientos \u2192 Compara \u2192 Ajusta \u2192 Concilia \u2192 Reporta",
        "cierre": "Revisa cuentas \u2192 Ajusta \u2192 Calcula impuestos \u2192 Cierra mes \u2192 Reporta",
        "cobranza": "Factura vence \u2192 Recuerda \u2192 Gestiona \u2192 Recibe \u2192 Concilia",
        "reporting": "Recopila datos \u2192 Clasifica \u2192 Calcula \u2192 Genera informe \u2192 Presenta",
        "otro": "",
    }),
    "rrhh": ("RRHH", "7", [
        ("", "Selecciona..."),
        ("seleccion", "Selecci\u00f3n y contrataci\u00f3n"),
        ("nomina", "N\u00f3mina y beneficios"),
        ("evaluacion", "Evaluaci\u00f3n de desempe\u00f1o"),
        ("clima", "Clima laboral"),
        ("capacitacion", "Capacitaci\u00f3n"),
        ("otro", "Otro (personalizado)"),
    ], {
        "seleccion": "Vacante \u2192 Publica \u2192 Recibe CVs \u2192 Preselecciona \u2192 Entrevista \u2192 Contrata",
        "nomina": "Registra novedades \u2192 Calcula \u2192 Genera n\u00f3mina \u2192 Paga \u2192 Reporta",
        "evaluacion": "Define metas \u2192 Eval\u00faa \u2192 Retroalimenta \u2192 Califica \u2192 Archiva",
        "clima": "Dise\u00f1a encuesta \u2192 Aplica \u2192 Analiza \u2192 Reporta \u2192 Plan de acci\u00f3n",
        "capacitacion": "Detecta necesidad \u2192 Dise\u00f1a \u2192 Ejecuta \u2192 Eval\u00faa \u2192 Certifica",
        "otro": "",
    }),
    "dir": ("Direcci\u00f3n Estrat\u00e9gica", "8", [
        ("", "Selecciona..."),
        ("planeacion", "Planeaci\u00f3n anual"),
        ("reporting", "Reporting gerencial"),
        ("metas", "Definici\u00f3n de metas / KPIs"),
        ("mercado", "An\u00e1lisis de mercado"),
        ("presupuesto", "Gesti\u00f3n presupuestal"),
        ("otro", "Otro (personalizado)"),
    ], {
        "planeacion": "Diagn\u00f3stico \u2192 Define objetivos \u2192 Planifica \u2192 Ejecuta \u2192 Mide",
        "reporting": "Recopila datos \u2192 Analiza \u2192 Prepara informe \u2192 Presenta \u2192 Decide",
        "metas": "Define KPI \u2192 Comunica \u2192 Da seguimiento \u2192 Eval\u00faa \u2192 Ajusta",
        "mercado": "Investiga \u2192 Analiza competencia \u2192 Identifica oportunidades \u2192 Reporta",
        "presupuesto": "Proyecta ingresos \u2192 Estima gastos \u2192 Asigna \u2192 Ejecuta \u2192 Controla",
        "otro": "",
    }),
}

def build_area(key, title, num, options, steps):
    opts = "\n".join([f'      <option value="{v}">{t}</option>' for v, t in options])
    return f"""  <h2>{title}</h2>
  <div style="margin-bottom:6px;">
    <label>{num}. Selecciona tu proceso principal de {title.lower()}</label>
    <select id="pyme-{key}-proceso" onchange="autoFillPasos('{key}',this.value)">
{opts}
    </select>
  </div>
  <div style="margin-bottom:6px;">
    <label>Pasos principales <span class="tag">(puedes ajustarlos)</span></label>
    <input type="text" id="pyme-{key}-pasos" placeholder="Ej: paso1 \u2192 paso2 \u2192 paso3">
  </div>
  <div style="margin-bottom:6px;">
    <label>\u00bfD\u00f3nde se pierde m\u00e1s tiempo o hay errores?</label>
    <textarea id="pyme-{key}-cuello" rows="1" placeholder="Ej: ah\u00ed se traba porque..."></textarea>
  </div>
  <div style="margin-bottom:6px;">
    <label>\u00bfC\u00f3mo te imaginas que deber\u00eda funcionar idealmente? <span class="tag">(opcional)</span></label>
    <textarea id="pyme-{key}-mejora" rows="1" placeholder="Si se te ocurre c\u00f3mo mejorarlo..."></textarea>
  </div>
"""

# Build areas
areas_html = ""
for key, (title, num, options, steps) in area_opts.items():
    areas_html += build_area(key, title, num, options, steps)

# Build autoFillPasos JS
steps_js_parts = []
for key, (title, num, options, steps) in area_opts.items():
    st = ", ".join([f'"{k}": "{v}"' for k, v in steps.items()])
    steps_js_parts.append(f'    {key}: {{{st}}}')
steps_js = ",\n".join(steps_js_parts)

# Full PYME HTML
pyme_html = f"""<!-- PREGUNTAS PYME -->
<div class="card hidden" data-section="pyme">
{areas_html}</div>

<!-- G. TECNOLOGIA Y EQUIPO -->
<div class="card hidden" data-section="pyme">
  <h2>G. Tecnolog\u00eda y equipo</h2>
  <div style="margin-bottom:10px;">
    <label>9. \u00bfCuentan con equipo o persona responsable de TI?</label>
    <div class="opciones" data-radio="ti">
      <div class="opcion" data-type="radio" onclick="toggleRadio(this,'ti')">S\u00ed, equipo interno de TI</div>
      <div class="opcion" data-type="radio" onclick="toggleRadio(this,'ti')">S\u00ed, una persona encargada (comparte funciones)</div>
      <div class="opcion" data-type="radio" onclick="toggleRadio(this,'ti')">Proveedor / consultor externo</div>
      <div class="opcion" data-type="radio" onclick="toggleRadio(this,'ti')">No contamos con soporte TI</div>
    </div>
  </div>
  <div style="margin-bottom:10px;">
    <label>10. Capacidad del equipo para implementar soluciones de IA</label>
    <div class="escala" data-escala="ti-cap">
      <div class="num" onclick="setEscala(this,'ti-cap')">1</div>
      <div class="num" onclick="setEscala(this,'ti-cap')">2</div>
      <div class="num" onclick="setEscala(this,'ti-cap')">3</div>
      <div class="num" onclick="setEscala(this,'ti-cap')">4</div>
      <div class="num" onclick="setEscala(this,'ti-cap')">5</div>
    </div>
    <div style="font-size:10px;color:#8B8176;margin-top:2px;text-align:center;">1 = sin personal \u00b7 3 = soporte b\u00e1sico \u00b7 5 = equipo con capacidad de integraciones</div>
  </div>
  <div style="margin-bottom:10px;">
    <label>11. \u00bfQu\u00e9 infraestructura tecnol\u00f3gica tiene la empresa para evaluar la opci\u00f3n de instalar IA local (modelos ejecutados en sus propios equipos o servidores)?</label>
    <div class="opciones" data-multi="infraestructura">
      <div class="opcion" data-type="multi" onclick="toggleOpcion(this)">Servidor propio en las instalaciones de la empresa</div>
      <div class="opcion" data-type="multi" onclick="toggleOpcion(this)">Servicios en la nube (AWS, Azure, Google Cloud)</div>
      <div class="opcion" data-type="multi" onclick="toggleOpcion(this)">Equipos con caracter\u00edsticas apropiadas (procesador, RAM, almacenamiento, VRAM)</div>
      <div class="opcion" data-type="multi" onclick="toggleOpcion(this)">Equipos est\u00e1ndar de oficina (sin capacidad para IA local)</div>
      <div class="opcion" data-type="multi" onclick="toggleOpcion(this)">No contamos con infraestructura para IA local</div>
      <div class="opcion" data-type="multi" onclick="toggleOpcion(this)">No lo s\u00e9 / necesito asesor\u00eda</div>
    </div>
  </div>
</div>
"""

# Replace PYME section
start_pyme = html.find('<!-- PREGUNTAS PYME -->')
end_pyme = html.find('<!-- NIVEL DE MADUREZ IA')
if start_pyme > -1 and end_pyme > -1:
    html = html[:start_pyme] + pyme_html + html[end_pyme:]
    print("PYME section: OK")
else:
    print("PYME markers: NOT FOUND")
    sys.exit(1)

# Add autoFillPasos JS before recolectar
pasos_func = f"""
function autoFillPasos(area, value) {{
  var stepsMap = {{
{steps_js}
  }};
  var input = document.getElementById('pyme-' + area + '-pasos');
  if (stepsMap[area] && stepsMap[area][value] !== undefined) {{
    input.value = stepsMap[area][value];
    if (value === 'otro') input.value = '';
  }}
}}
"""
html = html.replace("function recolectar()", pasos_func + "\nfunction recolectar()")
print("autoFillPasos JS: OK")

# Update recolectar for PYME fields
old_pyme_recolect = """    r['mv_proceso'] = document.getElementById('pyme-mv-proceso').value;
    r['mv_pasos'] = document.getElementById('pyme-mv-pasos').value;
    r['mv_cuello'] = document.getElementById('pyme-mv-cuello').value;
    r['mv_mejora'] = document.getElementById('pyme-mv-mejora').value;
    r['ops_proceso'] = document.getElementById('pyme-ops-proceso').value;
    r['ops_pasos'] = document.getElementById('pyme-ops-pasos').value;
    r['ops_cuello'] = document.getElementById('pyme-ops-cuello').value;
    r['ops_mejora'] = document.getElementById('pyme-ops-mejora').value;
    r['fin_proceso'] = document.getElementById('pyme-fin-proceso').value;
    r['fin_pasos'] = document.getElementById('pyme-fin-pasos').value;
    r['fin_cuello'] = document.getElementById('pyme-fin-cuello').value;
    r['fin_mejora'] = document.getElementById('pyme-fin-mejora').value;
    r['rrhh_proceso'] = document.getElementById('pyme-rrhh-proceso').value;
    r['rrhh_pasos'] = document.getElementById('pyme-rrhh-pasos').value;
    r['rrhh_cuello'] = document.getElementById('pyme-rrhh-cuello').value;
    r['rrhh_mejora'] = document.getElementById('pyme-rrhh-mejora').value;
    r['dir_proceso'] = document.getElementById('pyme-dir-proceso').value;
    r['dir_pasos'] = document.getElementById('pyme-dir-pasos').value;
    r['dir_cuello'] = document.getElementById('pyme-dir-cuello').value;
    r['dir_mejora'] = document.getElementById('pyme-dir-mejora').value;
    r['ti_equipo'] = [...document.querySelectorAll('[data-radio="ti"] .active')].map(e => e.textContent.trim()).join(', ');
    r['ti_capacidad'] = [...document.querySelectorAll('[data-escala="ti-cap"] .active')].map(e => e.textContent.trim()).join(', ');
    r['despliegue'] = [...document.querySelectorAll('[data-radio="despliegue"] .active')].map(e => e.textContent.trim()).join(', ');
    r['presupuesto'] = [...document.querySelectorAll('[data-radio="presupuesto"] .active')].map(e => e.textContent.trim()).join(', ');"""

new_pyme_recolect = """    r['mv_proceso'] = document.getElementById('pyme-mv-proceso').value;
    r['mv_pasos'] = document.getElementById('pyme-mv-pasos').value;
    r['mv_cuello'] = document.getElementById('pyme-mv-cuello').value;
    r['mv_mejora'] = document.getElementById('pyme-mv-mejora').value;
    r['ops_proceso'] = document.getElementById('pyme-ops-proceso').value;
    r['ops_pasos'] = document.getElementById('pyme-ops-pasos').value;
    r['ops_cuello'] = document.getElementById('pyme-ops-cuello').value;
    r['ops_mejora'] = document.getElementById('pyme-ops-mejora').value;
    r['fin_proceso'] = document.getElementById('pyme-fin-proceso').value;
    r['fin_pasos'] = document.getElementById('pyme-fin-pasos').value;
    r['fin_cuello'] = document.getElementById('pyme-fin-cuello').value;
    r['fin_mejora'] = document.getElementById('pyme-fin-mejora').value;
    r['rrhh_proceso'] = document.getElementById('pyme-rrhh-proceso').value;
    r['rrhh_pasos'] = document.getElementById('pyme-rrhh-pasos').value;
    r['rrhh_cuello'] = document.getElementById('pyme-rrhh-cuello').value;
    r['rrhh_mejora'] = document.getElementById('pyme-rrhh-mejora').value;
    r['dir_proceso'] = document.getElementById('pyme-dir-proceso').value;
    r['dir_pasos'] = document.getElementById('pyme-dir-pasos').value;
    r['dir_cuello'] = document.getElementById('pyme-dir-cuello').value;
    r['dir_mejora'] = document.getElementById('pyme-dir-mejora').value;
    r['ti_equipo'] = [...document.querySelectorAll('[data-radio="ti"] .active')].map(e => e.textContent.trim()).join(', ');
    r['ti_capacidad'] = [...document.querySelectorAll('[data-escala="ti-cap"] .active')].map(e => e.textContent.trim()).join(', ');
    r['infraestructura'] = [...document.querySelectorAll('[data-multi="infraestructura"] .active')].map(e => e.textContent.trim()).join(', ');"""

if old_pyme_recolect in html:
    html = html.replace(old_pyme_recolect, new_pyme_recolect)
    print("Recolectar PYME: OK")
else:
    print("Recolectar PYME: NOT FOUND")
    # Try to find what's in there
    idx = html.find("r['mv_proceso']")
    if idx > -1:
        print(f"  Found mv_proceso at {idx}")
        end = html.find("  }", idx)
        print(repr(html[idx:end+50]))
    sys.exit(1)

# Update descargar output
old_desc = "    txt += 'Despliegue: ' + (r.despliegue || '-') + '\\\\n';\n    txt += 'Presupuesto: ' + (r.presupuesto || '-') + '\\\\n\\\\n';"
new_desc = "    txt += 'Infraestructura: ' + (r.infraestructura || '-') + '\\\\n\\\\n';"
if old_desc in html:
    html = html.replace(old_desc, new_desc)
    print("Descargar: OK")
else:
    print("Descargar: NOT FOUND")
    print(f"  Found at: {html.find('Despliegue')}")

# Save
with open(r"C:\Users\User\Downloads\formulario-diagnostico-general\index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n=== VERIFICACION ===")
checks = {
    "CSS indicators": '.opcion[data-type="radio"]::before' in html,
    "PYME MV dropdown": 'pyme-mv-proceso' in html and 'onchange=' in html,
    "Mejora opcional": 'opcional' in html[html.find('pyme-mv-mejora'):html.find('pyme-mv-mejora')+200] if 'pyme-mv-mejora' in html else False,
    "Infraestructura Q11": 'data-multi="infraestructura"' in html,
    "No old despliegue": 'data-radio="despliegue"' not in html,
    "No old presupuesto": 'data-radio="presupuesto"' not in html,
    "autoFillPasos JS": 'autoFillPasos' in html,
    "data-type multi attr": 'data-type="multi"' in html,
    "div balance": html.count('<div') == html.count('</div>'),
}
ok = 0
for k, v in checks.items():
    ok += 1 if v else 0
    print(f"  {'OK' if v else 'FAIL'} {k}")
print(f"  -> {ok}/{len(checks)} checks passed")
if not checks["div balance"]:
    print(f"  Divs: <{html.count('<div')}> </{html.count('</div')}>")