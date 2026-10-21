"""
Generates the annex "Permisos por rol" (Markdown) from snapshots of the Airflows "Models" schema.
Usage: python gen_permisos.py <airflows-permisos.json> <airflows-models.json> <output.md>
"""
import json, sys, collections

P = json.load(open(sys.argv[1], encoding='utf-8'))
M = json.load(open(sys.argv[2], encoding='utf-8'))

E = {e['id']: e for e in M['Entity']}
ELab = collections.defaultdict(dict)
for x in M['EntityLabel']:
  ELab[x['container']][x['locale']] = x['label']
ALab = collections.defaultdict(dict)
for x in M['EntityAttributeLabel']:
  ALab[x['container']][x['locale']] = x['label']
A = {a['id']: a for a in M['EntityAttribute']}
X = {x['id']: x for x in M['ExternalEntity']}
R = {r['id']: r['name'] for r in P['Role']}

# Roles of the Cotown application (platform roles of Airflows are left out)
ROLES = [100, 101, 102, 103, 104, 105, 106, 200, 300, 400]
DESC = {
  100: 'Rol base de todo el personal de Cotown',
  101: 'Administración del sistema',
  102: 'Reservas',
  103: 'Marketing',
  104: 'Operaciones',
  105: 'Facturación',
  106: 'Vandor (contratos LAU y otros)',
  200: 'Propietarios (rol base)',
  300: 'Clientes (rol base)',
  400: 'Gestores externos (sin uso)',
}
ABBR = [('SELECT', 'L'), ('INSERT', 'A'), ('UPDATE', 'M'), ('DELETE', 'B'), ('EXPORT', 'E'), ('MENU', 'Me')]
SCHEMAS = ['Provider', 'Customer', 'Geo', 'Building', 'Resource', 'Booking', 'Billing', 'Marketing', 'Auxiliar', 'Batch', 'Admin']


def types(t):
  return set(x.strip() for x in (t or '').strip('{}').split(',') if x.strip())


def code(ts):
  return ' '.join(a for t, a in ABBR if t in ts) or '–'


def es(lab, fallback):
  return lab.get('es_ES') or lab.get('en_US') or fallback


perm = collections.defaultdict(dict)      # role -> entity -> types
for p in P['EntityPermission']:
  if p['entity'] in E:
    perm[p['role']][p['entity']] = types(p['types'])
attr = collections.defaultdict(list)      # role -> [(entity, attribute label, types)]
for p in P['EntityAttributePermission']:
  a = A.get(p['attribute'])
  if a:
    attr[p['role']].append((a['container'], es(ALab[a['id']], a['name']), types(p['types'])))
ext = collections.defaultdict(list)
for p in P['ExternalEntityPermission']:
  x = X.get(p['externalEntity'])
  if x:
    ext[p['role']].append(f"{x['schema']} › {x['name']}")
rls = collections.defaultdict(list)
for p in P['RowLevelPermission']:
  if p['entity'] in E:
    rls[p['role']].append((p['entity'], p['expression']))

out = []
w = out.append
w('# Anexo. Permisos por rol')
w('')
w('> Generado automáticamente a partir de la configuración de permisos de Airflows (esquema `Models`).')
w('')
w('Abreviaturas: **L** leer, **A** alta, **M** modificar, **B** borrar, **E** exportar, **Me** visible en el menú. '
  'Un usuario de personal tiene siempre el rol base `cotown` más sus roles funcionales; sus permisos son la suma de todos ellos.')
w('')
w('## Resumen por área')
w('')
MENUS = {'Provider': 'Propietarios', 'Customer': 'Clientes', 'Geo': 'Ubicaciones', 'Building': 'Edificios', 'Resource': 'Activos', 'Booking': 'Reservas', 'Billing': 'Facturación', 'Marketing': 'Marketing', 'Auxiliar': 'Auxiliares', 'Batch': 'Procesos', 'Admin': 'Administración'}
w('| Rol | Descripción | ' + ' | '.join(MENUS[x] for x in SCHEMAS) + ' |')
w('|---|---|' + '---|' * len(SCHEMAS))
for rid in ROLES:
  by_schema = collections.defaultdict(set)
  for eid, ts in perm[rid].items():
    by_schema[E[eid]['schema']] |= ts
  cells = [code(by_schema.get(s, set()) - {'MENU', 'EXPORT'}) for s in SCHEMAS]
  w(f'| `{R[rid]}` | {DESC[rid]} | ' + ' | '.join(cells) + ' |')
w('')
w('## Pantallas del backoffice complementario')
w('')
w('| Rol | Pantallas |')
w('|---|---|')
for rid in ROLES:
  if ext[rid]:
    w(f'| `{R[rid]}` | {", ".join(sorted(ext[rid]))} |')
w('')

for rid in ROLES:
  w(f'## Rol `{R[rid]}` — {DESC[rid]}')
  w('')
  if perm[rid]:
    w('| Entidad | Nombre en el ERP | Permisos |')
    w('|---|---|---|')
    for eid in sorted(perm[rid], key=lambda i: (E[i]['schema'], E[i]['name'])):
      w(f"| `{E[eid]['schema']}.{E[eid]['name']}` | {es(ELab[eid], E[eid]['name'])} | {code(perm[rid][eid])} |")
    w('')
  if attr[rid]:
    by_ent = collections.defaultdict(list)
    for eid, label, ts in attr[rid]:
      by_ent[eid].append(f"{label} ({code(ts)})")
    w('Campos que este rol puede informar o modificar (en el resto de campos de esas entidades, solo lectura):')
    w('')
    w('| Entidad | Campos |')
    w('|---|---|')
    for eid in sorted(by_ent, key=lambda i: (E[i]['schema'], E[i]['name']) if i in E else ('', '')):
      if eid in E:
        w(f"| `{E[eid]['schema']}.{E[eid]['name']}` | {', '.join(sorted(by_ent[eid]))} |")
    w('')
  if rls[rid]:
    filtered = [(e, x) for e, x in rls[rid] if (x or '').strip().upper() != 'TRUE']
    if filtered:
      w('Seguridad por fila: solo ve las filas propias en ' +
        ', '.join(sorted(f"`{E[e]['schema']}.{E[e]['name']}`" for e, _ in filtered)) + '.')
    else:
      w('Seguridad por fila: ve todas las filas.')
    w('')

open(sys.argv[3], 'w', encoding='utf-8').write('\n'.join(out))
print('ok', sys.argv[3], len(out), 'lines')
