import sys
from xml.sax.saxutils import quoteattr

# Colours (same legend as the original Experis diagram)
C_AIR = '#d5e8d4'   # Airflows
C_SQL = '#f8cecc'   # SQL
C_PY  = '#dae8fc'   # Python
C_NG  = '#fff2cc'   # Angular
C_WEB = '#e1d5e7'   # HTML/CSS/JS
C_11  = '#bac8d3'   # 11ty
C_EXT = '#ffffff'   # External
C_GRP = '#f5f5f5'   # Group
C_CLD = '#dae8fc'   # Cloud container

cells = []
n = [10]

def nid():
  n[0] += 1
  return f'c{n[0]}'

def box(label, x, y, w, h, fill, extra='', bold=False):
  i = nid()
  st = f'rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor=#666666;fontSize=11;{extra}'
  if bold: st += 'fontStyle=1;'
  cells.append(f'<mxCell id="{i}" value={quoteattr(label)} style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
  return i

def group(label, x, y, w, h, fill=C_GRP, dashed=False):
  st = f'rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor=#666666;verticalAlign=top;align=left;spacingLeft=6;fontStyle=1;fontSize=12;'
  if dashed: st += 'dashed=1;dashPattern=1 2;'
  i = nid()
  cells.append(f'<mxCell id="{i}" value={quoteattr(label)} style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
  return i

def cyl(label, x, y, w, h, fill):
  i = nid()
  st = f'shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;size=10;fillColor={fill};strokeColor=#666666;fontSize=11;'
  cells.append(f'<mxCell id="{i}" value={quoteattr(label)} style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
  return i

def actor(label, x, y):
  i = nid()
  st = 'shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=11;'
  cells.append(f'<mxCell id="{i}" value={quoteattr(label)} style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="24" height="44" as="geometry"/></mxCell>')
  return i

def edge(src, dst, label='', extra=''):
  i = nid()
  st = f'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;strokeColor=#333333;fontSize=10;labelBackgroundColor=#ffffff;{extra}'
  cells.append(f'<mxCell id="{i}" value={quoteattr(label)} style="{st}" edge="1" parent="1" source="{src}" target="{dst}"><mxGeometry relative="1" as="geometry"/></mxCell>')
  return i

# Users
a_staff = actor('Personal de Cotown', 118, 0)
a_pub   = actor('Público', 553, 0)
a_res   = actor('Residentes', 813, 0)

# Hetzner
group('Hetzner', 0, 80, 380, 600, C_CLD, dashed=True)
group('Airflows (core.cotown.com)', 15, 110, 350, 555)
b_ui   = box('Interfaz de usuario<br>(ERP de gestión)', 30, 145, 200, 50, C_AIR, bold=True)
b_bo   = box('Backoffice complementario<br><font style="font-size:9px">Planning, dashboards, informes</font>', 240, 145, 110, 110, C_NG)
b_sec  = box('Seguridad (Keycloak)', 30, 205, 200, 50, C_AIR)
b_api  = box('API GraphQL y ficheros', 30, 270, 320, 40, C_AIR)
b_trg  = box('Reglas de negocio<br>(triggers)', 30, 325, 200, 60, C_SQL)
b_cron = box('Procesos programados<br>(pg_cron)', 240, 325, 110, 60, C_AIR)
b_mod  = box('Modelo de datos<br>(metadatos)', 30, 410, 150, 80, C_AIR, extra='shape=mxgraph.bpmn.data;labelPosition=center;verticalLabelPosition=middle;')
b_db   = cyl('Base de datos<br>PostgreSQL', 200, 400, 150, 100, C_AIR)

# Azure
group('Azure', 420, 80, 560, 600, C_CLD, dashed=True)
g_srv  = group('Servidor de servicios (back.cotown.com)', 435, 110, 530, 450)
b_ngx  = box('Servidor web y HTTPS (nginx)', 450, 140, 500, 30, C_GRP)
g_web  = group('Webs comerciales', 450, 185, 240, 135)
b_cot  = box('cotown.com', 460, 215, 110, 30, C_WEB)
b_van  = box('vanguard-student-<br>housing.com', 460, 255, 110, 40, C_WEB)
b_gen  = box('Generador<br>(cada 2 h)', 580, 215, 100, 80, C_11)
g_prv  = group('Áreas privadas', 700, 185, 250, 135)
b_por  = box('Portal del residente', 710, 215, 230, 35, C_NG)
b_bkw  = box('Proceso de reserva web', 710, 260, 230, 35, C_PY)
g_int  = group('Servicio de integración (API)', 450, 335, 240, 170)
labels = ['Pagos con tarjeta', 'Dashboards e informes', 'Datos para las webs', 'API contable', 'Calendarios (iCal)']
for k, l in enumerate(labels):
  box(l, 460, 362 + k * 28, 220, 24, C_PY)
g_bat  = group('Procesos automáticos (cada 15 min)', 700, 335, 250, 170)
labels = ['Facturación', 'PDF de facturas', 'Contratos y firma', 'Cargas de Excel', 'Envío de emails']
for k, l in enumerate(labels):
  box(l, 710, 362 + k * 28, 230, 24, C_PY)
b_mon  = box('Monitorización (Grafana, Loki, Prometheus)', 450, 515, 500, 30, C_GRP)
g_dw   = group('Data warehouse (data.cotown.com)', 435, 575, 530, 95)
b_etl  = box('Carga de datos (ETL)', 450, 610, 200, 40, C_PY)
b_dw   = cyl('Data warehouse<br>PostgreSQL', 760, 600, 150, 60, C_PY)

# External services
g_ext  = group('Servicios externos', 1020, 80, 230, 600, '#ffffff', dashed=True)
ext = [
  ('<b>Redsys</b><br>Pagos con tarjeta', 115),
  ('<b>DocuSign</b><br>Firma de contratos', 170),
  ('<b>Pipedrive</b><br>CRM (leads)', 225),
  ('<b>Microsoft 365</b><br>Correo y SharePoint', 280),
  ('<b>SAP ByDesign</b><br>Contabilidad', 335),
  ('<b>Marketplaces</b><br>Disponibilidad (iCal)', 390),
]
ext_ids = [box(l, 1035, y, 200, 45, C_EXT) for l, y in ext]
b_pbi  = box('<b>Power BI</b><br>Analítica', 1035, 607, 200, 45, C_EXT)

# Edges
edge(a_staff, b_ui)
edge(a_pub, g_web)
edge(a_res, b_por)
edge(g_srv, b_api, 'GraphQL (HTTPS)', 'exitX=0;exitY=0.4;entryX=1;entryY=0.5;labelBackgroundColor=none;verticalAlign=bottom;')
edge(g_srv, b_db, 'SQL (túnel SSH)', 'exitX=0;exitY=0.7556;entryX=1;entryY=0.5;labelBackgroundColor=none;verticalAlign=bottom;')
edge(b_etl, b_db, 'SQL (túnel SSH)', 'exitX=0;exitY=0.5;entryX=0.5;entryY=1;')
edge(b_etl, b_dw, '', 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;')
edge(g_srv, g_ext, 'HTTPS / SMTP', 'exitX=1;exitY=0.4;entryX=0;entryY=0.35;startArrow=block;startFill=1;labelBackgroundColor=none;verticalAlign=bottom;')
edge(b_pbi, b_dw, '', 'exitX=0;exitY=0.5;entryX=1;entryY=0.5;')

# Legend
lx, ly = 0, 710
cells.append(f'<mxCell id="{nid()}" value="Leyenda:" style="text;html=1;fontStyle=1;fontSize=11;align=left;verticalAlign=middle;" vertex="1" parent="1"><mxGeometry x="{lx}" y="{ly}" width="60" height="20" as="geometry"/></mxCell>')
leg = [('Airflows', C_AIR), ('SQL', C_SQL), ('Python', C_PY), ('Angular', C_NG), ('HTML/CSS/JS', C_WEB), ('Eleventy', C_11), ('Servicio externo', C_EXT)]
x = lx + 70
for l, c in leg:
  box('', x, ly, 20, 20, c)
  cells.append(f'<mxCell id="{nid()}" value={quoteattr(l)} style="text;html=1;fontSize=11;align=left;verticalAlign=middle;" vertex="1" parent="1"><mxGeometry x="{x + 25}" y="{ly}" width="110" height="20" as="geometry"/></mxCell>')
  x += 145

xml = ('<mxfile host="Oimbra"><diagram id="arquitectura" name="Arquitectura"><mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1300" pageHeight="800" math="0" shadow="0"><root>'
       '<mxCell id="0"/><mxCell id="1" parent="0"/>' + ''.join(cells) + '</root></mxGraphModel></diagram></mxfile>')
open(sys.argv[1], 'w', encoding='utf-8').write(xml)
print('ok', len(cells))
