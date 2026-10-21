import sys
from xml.sax.saxutils import quoteattr

# Booking B2C lifecycle (states from Auxiliar.Booking_status; transitions from back/function/Booking.*)

W, H = 160, 54
CX, CY = 250, 150
X0, Y0 = 20, 70

F_PRE = '#f5f5f5'   # request phase
F_OK  = '#dae8fc'   # confirmed path
F_END = '#f8cecc'   # discarded / cancelled
F_FIN = '#d5e8d4'   # finished

K_SYS = '#1f6fb2'   # automatic (system)
K_STF = '#d9822b'   # staff
K_CUS = '#3c8d3c'   # customer

cells = []
n = [10]
pos = {}

def nid():
  n[0] += 1
  return f'c{n[0]}'

def state(key, label, code, col, row, fill, note=''):
  x, y = X0 + col * CX, Y0 + row * CY
  pos[key] = (x, y)
  v = f'<b>{label}</b><br><font style="font-size:9px;color:#555555">{code}</font>'
  if note:
    v += f'<br><font style="font-size:8px;color:#555555"><i>{note}</i></font>'
  st = f'rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor=#666666;fontSize=11;arcSize=20;'
  cells.append(f'<mxCell id="{key}" value={quoteattr(v)} style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{W}" height="{H + (14 if note else 0)}" as="geometry"/></mxCell>')

def edge(a, b, label, kind, extra='', points=None):
  st = (f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;endFill=1;strokeColor={kind};fontColor={kind};'
        f'strokeWidth=1.5;fontSize=9;labelBackgroundColor=#ffffff;{extra}')
  pts = ''
  if points:
    pts = '<Array as="points">' + ''.join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in points) + '</Array>'
  cells.append(f'<mxCell id="{nid()}" value={quoteattr(label)} style="{st}" edge="1" parent="1" source="{a}" target="{b}"><mxGeometry relative="1" as="geometry">{pts}</mxGeometry></mxCell>')

def text(v, x, y, w, h, extra=''):
  cells.append(f'<mxCell id="{nid()}" value={quoteattr(v)} style="text;html=1;fontSize=11;align=left;verticalAlign=middle;whiteSpace=wrap;{extra}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')

# Row 0: request, unpaid
state('sol',  'Solicitud',          'solicitud',          0, 0, F_PRE)
state('alt',  'Alternativas',       'alternativas',       1, 0, F_PRE)
state('pp',   'Pendiente de pago',  'pendientepago',      2, 0, F_PRE)
state('cad',  'Caducada',           'caducada',           3, 0, F_END)
state('des',  'Descartada',         'descartada',         4, 0, F_END, 'Botón «Activar»: vuelve a solicitud')
# Row 1: request, paid
state('solp', 'Solicitud pagada',   'solicitudpagada',    0, 1, F_PRE)
state('altp', 'Alternativas pagada','alternativaspagada', 1, 1, F_PRE)
state('conf', 'Confirmada',         'confirmada',         2, 1, F_OK)
state('desp', 'Descartada pagada',  'descartadapagada',   4, 1, F_END, 'Pendiente de devolver el booking fee')
# Row 2: documentation, deposit, contract
state('dko',  'Documentación KO',   'documentacionko',    1, 2, F_END)
state('dok',  'Documentación OK',   'documentacionok',    2, 2, F_OK)
state('fc',   'Firma de contrato',  'firmacontrato',      3, 2, F_OK)
state('con',  'Contrato',           'contrato',           4, 2, F_OK)
# Row 3: stay (right to left)
state('cic',  'Check-in confirmado','checkinconfirmado',  4, 3, F_OK)
state('ci',   'Check-in',           'checkin',            3, 3, F_OK)
state('ih',   'In house',           'inhouse',            2, 3, F_OK)
state('co',   'Check-out',          'checkout',           1, 3, F_OK)
state('rev',  'Revisión',           'revision',           0, 3, F_OK)
# Row 4: closing
state('dg',   'Devolver garantía',  'devolvergarantia',   0, 4, F_OK)
state('fin',  'Finalizada',         'finalizada',         1, 4, F_FIN)
state('can',  'Cancelada',          'cancelada',          3, 4, F_END, 'Desde cualquier estado, a mano')

top = Y0 - 30
# Request phase
edge('sol', 'alt', 'Propone alternativas', K_STF, 'exitX=1;exitY=0.3;entryX=0;entryY=0.3;')
edge('alt', 'sol', 'Acepta una', K_CUS, 'exitX=0;exitY=0.75;entryX=1;entryY=0.75;')
edge('solp', 'altp', 'Propone alternativas', K_STF, 'exitX=1;exitY=0.3;entryX=0;entryY=0.3;')
edge('altp', 'solp', 'Acepta una', K_CUS, 'exitX=0;exitY=0.75;entryX=1;entryY=0.75;')
edge('sol', 'solp', 'Paga booking fee', K_CUS, 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;')
edge('alt', 'altp', 'Paga booking fee', K_CUS, 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;')
edge('sol', 'pp', 'Asigna recurso', K_STF, 'exitX=0.5;exitY=0;entryX=0.5;entryY=0;',
     [(pos['sol'][0] + W / 2, top), (pos['pp'][0] + W / 2, top)])
edge('alt', 'pp', 'Asigna recurso', K_STF, 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;')
edge('pp', 'cad', 'Vence el plazo (2 días)', K_SYS, 'exitX=1;exitY=0.3;entryX=0;entryY=0.3;')
edge('cad', 'pp', 'Amplía el plazo', K_STF, 'exitX=0;exitY=0.75;entryX=1;entryY=0.75;')
edge('cad', 'des', '5 días sin ampliar', K_SYS, 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;')
edge('pp', 'conf', 'Paga booking fee', K_CUS, 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;')
edge('altp', 'conf', 'Asigna recurso', K_STF, 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;')
ybelow = pos['solp'][1] + H + 22
edge('solp', 'conf', 'Asigna recurso', K_STF, 'exitX=0.5;exitY=1;entryX=0;entryY=0.85;',
     [(pos['solp'][0] + W / 2, ybelow), (pos['conf'][0] - 20, ybelow), (pos['conf'][0] - 20, pos['conf'][1] + H * 0.85)])
edge('desp', 'des', 'Devuelve booking fee', K_STF, 'exitX=0.5;exitY=0;entryX=0.5;entryY=1;')

# Documentation, deposit, contract
edge('conf', 'dok', 'Documentación aprobada', K_STF, 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;')
yk = ybelow + 32
edge('conf', 'dko', 'Vence el plazo (14 días)', K_SYS, 'exitX=0.2;exitY=1;entryX=0.5;entryY=0;',
     [(pos['conf'][0] + W * 0.2, yk), (pos['dko'][0] + W / 2, yk)])
edge('conf', 'desp', 'Garantía impagada', K_SYS, 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;')
edge('dok', 'fc', 'Paga la garantía', K_CUS, 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;')
edge('fc', 'con', 'Firma (DocuSign)', K_CUS, 'exitX=1;exitY=0.3;entryX=0;entryY=0.3;')
edge('con', 'fc', 'Firma anulada', K_SYS, 'exitX=0;exitY=0.75;entryX=1;entryY=0.75;')

# Stay
edge('con', 'cic', 'Indica fecha de llegada', K_CUS, 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;')
edge('cic', 'ci', 'Llega la fecha', K_SYS, 'exitX=0;exitY=0.5;entryX=1;entryY=0.5;')
edge('ci', 'ih', 'Check-in OK', K_STF, 'exitX=0;exitY=0.5;entryX=1;entryY=0.5;')
edge('ih', 'co', 'Llega la fecha de salida', K_SYS, 'exitX=0;exitY=0.5;entryX=1;entryY=0.5;')
edge('co', 'rev', 'Inicia revisión', K_STF, 'exitX=0;exitY=0.5;entryX=1;entryY=0.5;')
edge('rev', 'dg', 'Revisión OK', K_STF, 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;')
edge('dg', 'fin', 'Garantía devuelta', K_STF, 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;')

# Title and legend
text('<b>Ciclo de vida de la reserva B2C</b>', X0, 0, 400, 24, 'fontSize=14;')
ly = Y0 + 5 * CY - 10
text('<b>Transición provocada por:</b>', X0, ly, 190, 20)
lx = X0 + 200
for label, k in [('el sistema (automático)', K_SYS), ('el personal de Cotown', K_STF), ('el cliente', K_CUS)]:
  cells.append(f'<mxCell id="{nid()}" value="" style="endArrow=block;endFill=1;html=1;strokeColor={k};strokeWidth=1.5;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{lx}" y="{ly + 10}" as="sourcePoint"/><mxPoint x="{lx + 40}" y="{ly + 10}" as="targetPoint"/></mxGeometry></mxCell>')
  text(label, lx + 48, ly, 160, 20)
  lx += 220
text('Botón «Descartar»: desde solicitud, alternativas o pendiente de pago pasa a <i>Descartada</i>; '
     'desde solicitud o alternativas pagada, a <i>Descartada pagada</i>. '
     '<i>Garantía impagada</i>: entrada en menos de 30 días y garantía emitida hace más de 4 días sin pagar.',
     X0, ly + 28, 960, 34, 'fontSize=10;fontColor=#555555;')

xml = ('<mxfile host="Oimbra"><diagram id="ciclo" name="Ciclo de vida B2C"><mxGraphModel dx="1200" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="900" math="0" shadow="0"><root>'
       '<mxCell id="0"/><mxCell id="1" parent="0"/>' + ''.join(cells) + '</root></mxGraphModel></diagram></mxfile>')
open(sys.argv[1], 'w', encoding='utf-8').write(xml)
print('ok', len(cells))
