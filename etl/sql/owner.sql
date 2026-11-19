SELECT DISTINCT
  p."Document" AS "id",
  CASE p."Document"
    WHEN 'A88445762' THEN 'Vandor'
    WHEN 'A88624408' THEN 'Matritense'
    WHEN 'B67551754' THEN 'Cotown'
    ELSE 'Third party'
  END AS "type",
  CASE p."Document"
    WHEN 'A88445762' THEN 1
    WHEN 'A88624408' THEN 2
    WHEN 'B67551754' THEN 3
    ELSE 4
  END AS "order",
  p."Name" AS "name"
FROM "Provider"."Provider" p
  INNER JOIN "Resource"."Resource" r ON r."Owner_id" = p.id;
