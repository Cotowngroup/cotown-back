import psycopg2, psycopg2.extras, json, sys, datetime
T = ['Application','ApplicationLabel','Dashboard','DashboardLabel','Entity','EntityLabel','EntityAttribute','EntityAttributeLabel',
     'EntityAttributeTooltip','EntityGroup','EntityGroupLabel','EntityKey','EntityReference','EntityReferenceAttribute','EntityTab',
     'EntityTabLabel','EnumType','EnumTypeLabel','ErrorMessage','ErrorMessageLabel','ExternalEntity','ExternalEntityLabel','Function',
     'IntelligenceFeature','IntelligenceModel','Question','QuestionLabel','Report','ReportTrigger','System','PythonPackage']
c = psycopg2.connect(host='127.0.0.1', port=15432, dbname='niledb', user='readonly', password='readonly', connect_timeout=15)
c.set_session(readonly=True); cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
out = {}
for t in T:
  try:
    cur.execute(f'SELECT * FROM "Models"."{t}"'); rows = cur.fetchall()
    for r in rows:
      r.pop('model', None); r.pop('training', None); r.pop('trainingResult', None)
    out[t] = rows; print(t, len(rows))
  except Exception as e:
    c.rollback(); print(t, 'ERROR', str(e).splitlines()[0])
json.dump(out, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, default=str, indent=1)
