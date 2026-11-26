"""
Generates the schema.txt of the MCP server for the Airflows database (niledb) from the Excel export of the
Airflows "Models" schema (modelo vAAAA.MM.DD.xls). Needs xlrd.
Usage: python gen_schema_core.py <modelo.xls> <schema-core.txt>
"""
import collections, sys
import xlrd

# Schemas not exposed by the MCP (the mcp_ro role cannot read them)
EXCLUDED = {'Batch'}

# Columns that every table has, filled in by the platform
STANDARD = {
  'id': 'Identificador',
  'Created_at': 'Fecha y hora de creación del registro',
  'Created_by': 'Usuario que creó el registro',
  'Updated_at': 'Fecha y hora de la última modificación del registro',
  'Updated_by': 'Usuario que modificó el registro por última vez',
}
HIDDEN = {'Search'}

wb = xlrd.open_workbook(sys.argv[1])


# Rows of a sheet as dicts: row 0 is the Models table name, row 1 the column names
def sheet(name):
  s = wb.sheet_by_name(name)
  head = [str(c.value) for c in s.row(1)]
  rows = []
  for r in range(2, s.nrows):
    row = {}
    for h, c in zip(head, s.row(r)):
      if h:
        v = c.value
        row[h] = int(v) if isinstance(v, float) and v.is_integer() else v
    rows.append(row)
  return rows


def text(v):
  return ' '.join(str(v or '').replace('"', "'").split())


def flag(v):
  return str(v) in ('1', 'True', 'true')


E      = {e['id']: e for e in sheet('Entity')}
ELabel = {x['container']: x['label'] for x in sheet('EntityLabel (ES)')}
ALabel = {x['container']: x['label'] for x in sheet('EntityAttributeLabel (ES)')}
Enum   = {e['id']: e for e in sheet('EnumType')}
key2ent = {k['id']: k['container'] for k in sheet('EntityKey')}

attrs = collections.defaultdict(list)
for a in sheet('EntityAttribute'):
  attrs[a['container']].append(a)
refs = collections.defaultdict(dict)
for r in sheet('EntityReference'):
  refs[r['container']][r['name']] = r


def sqltype(a):
  t = a['type']
  if a.get('enumType') in Enum:
    en = Enum[a['enumType']]
    t = f'"{en["schema"]}"."{en["name"]}"'
  elif t == 'DECIMAL' and a.get('precision') != '':
    t = f'NUMERIC({a["precision"]},{a["scale"] or 0})'
  elif t == 'TEXT' and a.get('length') != '':
    t = f'VARCHAR({a["length"]})'
  return t + ('[]' if flag(a.get('isArray')) else '')


def field(e, a):
  name = a['name']
  if name == 'id':
    return f'- "id": {sqltype(a)}, PK, "Identificador de {text(ELabel.get(e["id"])).lower() or e["name"]}"'
  parts = [text(ALabel.get(a['id'])) or STANDARD.get(name, '')]
  if text(a.get('documentation')):
    parts.append(text(a['documentation']))
  if a.get('enumType') in Enum:
    values = str(Enum[a['enumType']]['values']).strip('{}').replace(',', ', ')
    parts.append(f'Valores: {values}')
  r = refs[e['id']].get(name)
  target = E.get(key2ent.get(r['referencedKey'])) if r else None
  if target:
    parts.append(f'Referencia a {target["schema"]}.{target["name"]}.id')
  if flag(a.get('isAction')):
    parts.append('Botón de acción del ERP, sin datos de negocio')
  if a['type'] == 'DOCUMENT':
    parts.append('Documento gestionado por Airflows, no legible por SQL')
  null = 'NOT NULL' if flag(a.get('isRequired')) else 'NULL'
  return f'- "{name}": {sqltype(a)}, {null}, "{". ".join(p.rstrip(".") for p in parts if p)}"'


blocks = []
for e in sorted(E.values(), key=lambda e: (e['schema'], e['name'])):
  if e['schema'] in EXCLUDED:
    continue
  desc = '. '.join(p.rstrip('.') for p in (text(ELabel.get(e['id'])), text(e.get('documentation'))) if p)
  lines = [f'Table: "{e["schema"]}"."{e["name"]}"', f'Description: "{desc}"', 'Fields:']
  order = lambda a: (a['name'] != 'id', a['name'] in STANDARD, a['order'] if a['order'] != '' else 9999, a['name'])
  lines += [field(e, a) for a in sorted(attrs[e['id']], key=order) if a['name'] not in HIDDEN]
  blocks.append('\n'.join(lines))

open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write('\n\n'.join(blocks) + '\n')
print('ok', sys.argv[2], len(blocks), 'tablas', sum(b.count('\n- ') for b in blocks), 'columnas')
