"""
Generates the data dictionary annex (Markdown) from a snapshot of the Airflows "Models" schema.
Usage: python gen_diccionario.py <airflows-models.json> <output.md>
"""
import json, sys, collections

d = json.load(open(sys.argv[1], encoding='utf-8'))

def labels(table, key='label'):
  out = collections.defaultdict(dict)
  for x in d[table]:
    out[x['container']][x['locale']] = x.get(key)
  return out

E      = {e['id']: e for e in d['Entity']}
ELab   = labels('EntityLabel')
ALab   = labels('EntityAttributeLabel')
AppLab = labels('ApplicationLabel')
Enum   = {e['id']: e for e in d['EnumType']}
key2ent = {k['id']: k['container'] for k in d['EntityKey']}

def es(lab):
  return (lab or {}).get('es_ES') or (lab or {}).get('en_US') or ''

def clean(s):
  return (s or '').replace('\n', ' ').replace('|', '/').strip()

attrs = collections.defaultdict(list)
for a in d['EntityAttribute']:
  attrs[a['container']].append(a)
refs = collections.defaultdict(list)
for r in d['EntityReference']:
  refs[r['container']].append(r)

STANDARD = {'id', 'Created_at', 'Created_by', 'Updated_at', 'Updated_by', 'Search'}

TYPES = {'TEXT': 'Texto', 'TIMESTAMP': 'Fecha y hora', 'INTEGER': 'Entero', 'DECIMAL': 'Decimal', 'SERIAL': 'Identificador',
         'BOOLEAN': 'Sí/No', 'DATE': 'Fecha', 'DOCUMENT': 'Documento', 'TIME': 'Hora', 'POINT': 'Coordenadas'}

app_order = {a['name']: (a['order'] or 0) for a in d['Application']}
schemas = sorted({e['schema'] for e in E.values()}, key=lambda s: app_order.get(s, 999))
app_label = {a['name']: es(AppLab.get(a['id'])) for a in d['Application']}

out = []
w = out.append
w('# Anexo. Diccionario de datos')
w('')
w('> Generado automáticamente a partir de los metadatos de Airflows (esquema `Models`). No editar a mano: '
  'se regenera a partir de los metadatos cuando cambia el modelo.')
w('')
w(f'{len(E)} entidades y {len(d["EntityAttribute"])} atributos, agrupados por esquema. '
  'Para cada atributo: nombre técnico, etiqueta en el ERP, tipo, si es obligatorio (●) y, en su caso, '
  'la entidad a la que referencia o los valores posibles. '
  'Se omiten los campos que tienen todas las entidades (`id`, `Created_at`, `Created_by`, `Updated_at`, `Updated_by` y `Search`), '
  'descritos en el capítulo *Modelo de datos*, apartado *Convenciones*.')
w('')

for s in schemas:
  ents = sorted([e for e in E.values() if e['schema'] == s], key=lambda e: (e['order'] or 0, e['name']))
  w(f'## Esquema `{s}` — {app_label.get(s) or s}')
  w('')
  figs = [f'ER {s} {p}' for p in ('B2C', 'B2B', 'LAU')] if s == 'Booking' else [f'ER {s}']
  for f in figs:
    w(f"![{f}](../diagramas/er/{f.replace(' ', '%20')}.png)")
    w('')
  w('| Entidad | Nombre en el ERP | Descripción |')
  w('|---|---|---|')
  for e in ents:
    w(f"| `{e['name']}` | {clean(es(ELab.get(e['id'])))} | {clean(e.get('documentation'))} |")
  w('')
  for e in ents:
    w(f"### `{s}.{e['name']}` — {clean(es(ELab.get(e['id'])))}")
    w('')
    if e.get('documentation'):
      w(clean(e['documentation']))
      w('')
    ref_by_name = {r['name']: r for r in refs[e['id']]}
    w('| Atributo | Etiqueta | Tipo | Oblig. | Referencia / valores |')
    w('|---|---|---|---|---|')
    for a in sorted([a for a in attrs[e['id']] if a['name'] not in STANDARD], key=lambda a: (a['order'] if a['order'] is not None else 9999, a['name'])):
      t = TYPES.get(a['type'], a['type'] or '')
      if a.get('isArray'):
        t += ' (lista)'
      extra = ''
      if a.get('enumType') in Enum:
        en = Enum[a['enumType']]
        extra = ', '.join(en['values'] or [])
        t = 'Lista de valores'
      r = ref_by_name.get(a['name'])
      if r:
        tgt = E.get(key2ent.get(r['referencedKey']))
        if tgt:
          extra = f"→ `{tgt['schema']}.{tgt['name']}`"
      req = '●' if a.get('isRequired') else ''
      w(f"| `{a['name']}` | {clean(es(ALab.get(a['id'])))} | {t} | {req} | {clean(extra)} |")
    # references that are not plain attributes (multiple references)
    extra_refs = [r for r in refs[e['id']] if r['name'] not in {a['name'] for a in attrs[e['id']]}]
    for r in extra_refs:
      tgt = E.get(key2ent.get(r['referencedKey']))
      if tgt:
        w(f"| `{r['name']}` | | Referencia | | → `{tgt['schema']}.{tgt['name']}` |")
    w('')

open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(out))
print('ok', sys.argv[2], len(out), 'lines')
