"""
Generates ER diagrams (draw.io) from the Airflows "Models" snapshot:
  - one general diagram with the main entities and key relations
  - one diagram per schema
Layered layout: referenced entities above, referencing entities below; barycentre ordering to reduce crossings.
Usage: python gen_er.py <airflows-models.json> <output dir>
"""
import json, sys, os, collections
from xml.sax.saxutils import quoteattr

d = json.load(open(sys.argv[1], encoding='utf-8'))
OUT = sys.argv[2]

E = {e['id']: e for e in d['Entity']}
FQ = {f"{e['schema']}.{e['name']}": e['id'] for e in E.values()}
lab = collections.defaultdict(dict)
for x in d['EntityLabel']:
  lab[x['container']][x['locale']] = x['label']
applab = collections.defaultdict(dict)
for x in d['ApplicationLabel']:
  applab[x['container']][x['locale']] = x['label']
APP = {a['name']: applab[a['id']].get('es_ES', a['name']) for a in d['Application']}
key2ent = {k['id']: k['container'] for k in d['EntityKey']}

REL = set()
for r in d['EntityReference']:
  p = key2ent.get(r['referencedKey'])
  if p in E and r['container'] in E and p != r['container']:
    REL.add((r['container'], p))

FILL = {'Geo': '#d5e8d4', 'Building': '#d5e8d4', 'Resource': '#d5e8d4',
        'Customer': '#fff2cc', 'Provider': '#fff2cc',
        'Booking': '#dae8fc', 'Billing': '#f8cecc',
        'Marketing': '#e1d5e7', 'Auxiliar': '#eeeeee', 'Admin': '#eeeeee', 'Batch': '#eeeeee'}
W, H = 180, 46
CX, CY = 215, 120
MAXW = 9

# Main entities of other schemas that may appear (dashed) in a schema diagram
MAIN = {FQ[x] for x in ['Geo.Location', 'Geo.District', 'Building.Building', 'Resource.Resource', 'Customer.Customer',
                        'Provider.Provider', 'Provider.Agent', 'Booking.Booking', 'Booking.Booking_group',
                        'Booking.Booking_other', 'Billing.Invoice', 'Billing.Payment', 'Billing.Product',
                        'Billing.Promotion', 'Resource.Resource_flat_type', 'Resource.Resource_place_type']}

def es(i):
  return lab[i].get('es_ES') or E[i]['name']

def layout(nodes, edges):
  """nodes: iterable of ids; edges: set of (child, parent). Returns {id: (x, y)}."""
  nodes = list(nodes)
  parents = collections.defaultdict(set); children = collections.defaultdict(set)
  for c, p in edges:
    parents[c].add(p); children[p].add(c)
  memo = {}
  def level(n, stack=()):
    if n in memo: return memo[n]
    if n in stack: return 0
    ps = [p for p in parents[n] if p in nodes]
    memo[n] = 0 if not ps else 1 + max(level(p, stack + (n,)) for p in ps)
    return memo[n]
  for n in nodes:
    level(n)
  # Pull every node down to just above its highest child (shortens edges from top-level roots)
  for _ in range(len(nodes)):
    changed = False
    for n in nodes:
      cs = [c for c in children[n] if c in memo]
      if cs:
        target = min(memo[c] for c in cs) - 1
        ps = [p for p in parents[n] if p in memo]
        if ps:
          target = max(target, max(memo[p] for p in ps) + 1)
        if target > memo[n]:
          memo[n] = target; changed = True
    if not changed:
      break
  layers = collections.defaultdict(list)
  for n in sorted(nodes, key=lambda n: E[n]['name']):
    layers[memo[n]].append(n)
  # Split wide layers into rows
  rows = []
  for k in sorted(layers):
    L = layers[k]
    for s in range(0, len(L), MAXW):
      rows.append(L[s:s + MAXW])
  idx = {}
  def reindex():
    for r in rows:
      for i, n in enumerate(r):
        idx[n] = i - (len(r) - 1) / 2
  reindex()
  for _ in range(12):
    for ri in range(1, len(rows)):
      rows[ri].sort(key=lambda n: (sum(idx[p] for p in parents[n] if p in idx) / max(1, len([p for p in parents[n] if p in idx]))) if any(p in idx for p in parents[n]) else idx[n])
      reindex()
    for ri in range(len(rows) - 2, -1, -1):
      rows[ri].sort(key=lambda n: (sum(idx[c] for c in children[n] if c in idx) / max(1, len([c for c in children[n] if c in idx]))) if any(c in idx for c in children[n]) else idx[n])
      reindex()
  width = max(len(r) for r in rows)
  pos = {}
  for ri, r in enumerate(rows):
    off = (width - len(r)) / 2
    for i, n in enumerate(r):
      pos[n] = ((off + i) * CX, ri * CY)
  return pos

class Diagram:
  def __init__(self):
    self.cells = []; self.n = 10
  def nid(self):
    self.n += 1; return f'c{self.n}'
  def entity(self, i, x, y, external=False):
    e = E[i]
    v = f"<b>{es(i)}</b><br><font style=\"font-size:9px;color:#555555\">{e['schema']}.{e['name']}</font>"
    fill = '#ffffff' if external else FILL.get(e['schema'], '#ffffff')
    dash = 'dashed=1;' if external else ''
    st = f'rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor=#666666;fontSize=11;arcSize=12;{dash}'
    self.cells.append(f'<mxCell id="e{i}" value={quoteattr(v)} style="{st}" vertex="1" parent="1"><mxGeometry x="{x:.0f}" y="{y:.0f}" width="{W}" height="{H}" as="geometry"/></mxCell>')
  def rel(self, child, parent):
    st = 'html=1;endArrow=ERmandOne;startArrow=ERmany;endFill=0;startFill=0;strokeColor=#555555;rounded=0;'
    self.cells.append(f'<mxCell id="{self.nid()}" value="" style="{st}" edge="1" parent="1" source="e{child}" target="e{parent}"><mxGeometry relative="1" as="geometry"/></mxCell>')
  def text(self, v, x, y, w, h, size=14):
    self.cells.append(f'<mxCell id="{self.nid()}" value={quoteattr(v)} style="text;html=1;fontSize={size};align=left;verticalAlign=middle;whiteSpace=wrap;" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
  def save(self, path, name):
    xml = (f'<mxfile host="Oimbra"><diagram id="er" name={quoteattr(name)}><mxGraphModel grid="1" gridSize="10" page="0"><root>'
           '<mxCell id="0"/><mxCell id="1" parent="0"/>' + ''.join(self.cells) + '</root></mxGraphModel></diagram></mxfile>')
    open(path, 'w', encoding='utf-8').write(xml)

def draw(nodes, edges, external, title, path, legend):
  pos = layout(nodes, edges)
  g = Diagram()
  g.text(title, 0, -60, 900, 30, 16)
  for n, (x, y) in pos.items():
    g.entity(n, x, y, external=n in external)
  for c, p in sorted(edges):
    g.rel(c, p)
  maxy = max(y for _, y in pos.values()) + H + 30
  g.text(legend, 0, maxy, 1100, 30, 11)
  g.save(path, os.path.basename(path)[:-7])

LEG = ('Cada línea une la entidad que referencia (extremo múltiple) con la referenciada (extremo simple). '
       'Colores: verde inventario, amarillo personas y empresas, azul reservas, rojo precios y facturación. '
       'Con borde discontinuo, entidades de otras áreas.')
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- General diagram (curated)
GEN_EDGES = [
  ('Geo.District', 'Geo.Location'), ('Building.Building', 'Geo.District'), ('Resource.Resource', 'Building.Building'),
  ('Resource.Resource', 'Provider.Provider'), ('Resource.Resource', 'Billing.Pricing_rate'),
  ('Resource.Resource_availability', 'Resource.Resource'), ('Billing.Pricing_detail', 'Building.Building'),
  ('Booking.Booking', 'Resource.Resource'), ('Booking.Booking', 'Customer.Customer'), ('Booking.Booking', 'Provider.Agent'),
  ('Booking.Booking', 'Billing.Promotion'),
  ('Booking.Booking_option', 'Booking.Booking'), ('Booking.Booking_price', 'Booking.Booking'),
  ('Booking.Booking_service', 'Booking.Booking'),
  ('Booking.Booking_group', 'Customer.Customer'), ('Booking.Booking_group_rooms', 'Booking.Booking_group'),
  ('Booking.Booking_group_rooms', 'Resource.Resource'), ('Booking.Booking_group_rooming', 'Booking.Booking_group'),
  ('Booking.Booking_other', 'Resource.Resource'), ('Booking.Booking_other', 'Customer.Customer'),
  ('Customer.Customer_doc', 'Customer.Customer'),
  ('Billing.Invoice', 'Customer.Customer'), ('Billing.Invoice', 'Provider.Provider'), ('Billing.Invoice', 'Booking.Booking'),
  ('Billing.Invoice', 'Billing.Payment'), ('Billing.Invoice_line', 'Billing.Invoice'), ('Billing.Invoice_line', 'Billing.Product'),
  ('Billing.Payment', 'Customer.Customer'),
]
ge = {(FQ[c], FQ[p]) for c, p in GEN_EDGES}
gn = {n for e in ge for n in e}
draw(gn, ge, set(), '<b>Modelo de datos – visión general</b>', os.path.join(OUT, 'ER general.drawio'), LEG)
print('general', len(gn), len(ge))

# ---------------------------------------------------------------- One diagram per schema (Booking split in three)
def booking_part(name):
  if name.startswith('Booking_group'):
    return 'B2B'
  if name.startswith('Booking_other'):
    return 'LAU'
  return 'B2C'

SUBTITLE = {'B2C': 'Reservas B2C', 'B2B': 'Reservas B2B', 'LAU': 'Reservas LAU y otros'}
parts = []
for schema in sorted({e['schema'] for e in E.values()}):
  if schema == 'Booking':
    for p in ('B2C', 'B2B', 'LAU'):
      parts.append((schema, p, {i for i, e in E.items() if e['schema'] == schema and booking_part(e['name']) == p}))
  else:
    parts.append((schema, None, {i for i, e in E.items() if e['schema'] == schema}))

for schema, part, own in parts:
  edges = set(); ext = set()
  for c, p in REL:
    if c in own and p in own:
      edges.add((c, p))
    elif c in own and p in MAIN:
      edges.add((c, p)); ext.add(p)
    elif p in own and c in MAIN:
      edges.add((c, p)); ext.add(c)
  nodes = own | ext
  if schema == 'Auxiliar':
    # Catalogues referenced from everywhere: show only internal relations
    edges = {(c, p) for c, p in edges if c in own and p in own}; nodes = own; ext = set()
  title = SUBTITLE[part] if part else APP.get(schema, schema)
  fname = f'ER {schema}' + (f' {part}' if part else '')
  draw(nodes, edges, ext, f'<b>Modelo de datos – {title}</b> <font style="font-size:11px;color:#555555">(esquema {schema})</font>',
       os.path.join(OUT, f'{fname}.drawio'), LEG)
  print(fname, 'own', len(own), 'ext', len(ext), 'edges', len(edges))
