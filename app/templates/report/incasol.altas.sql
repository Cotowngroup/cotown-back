-- Altas Incasol B2C (reservas individuales con fianza legal)
WITH
altas AS (
  SELECT
    b.id::text                                        AS "Id",
    r."Code"                                          AS "Resource",
    COALESCE(r."Street", f."Street")                  AS "Street",
    COALESCE(f."Address", r."Address")                AS "Address",
    bu."Zip"                                          AS "Zip",
    l."Name"                                          AS "City",
    COALESCE(r."Registry_code", f."Registry_code", bu."Cadastral_ref") AS "Cadastral_ref",
    COALESCE(r."Area_woc", f."Area_woc")              AS "Area",
    COALESCE(r."Occupancy_certificate", f."Occupancy_certificate") AS "Occupancy_certificate",
    c."Name"                                          AS "Customer_name",
    c."Document"                                      AS "Customer_document",
    p."Name"                                          AS "Owner_name",
    p."Document"                                      AS "Owner_document",
    CONCAT_WS(', ', p."Address", p."Zip", p."City")   AS "Owner_address",
    b."Incasol_deposit"                               AS "Incasol_deposit",
    b."Contract_signed"                               AS "Contract_signed",
    b.id                                              AS "Sort_id"
  FROM "Booking"."Booking" b
    INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
    LEFT JOIN "Resource"."Resource" f ON f.id = r."Flat_id"
    INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id"
    LEFT JOIN "Geo"."District" d ON d.id = bu."District_id"
    LEFT JOIN "Geo"."Location" l ON l.id = d."Location_id"
    LEFT JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
    LEFT JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
  WHERE b."Contract_signed" >= %(fdesde)s AND b."Contract_signed" < %(fhasta)s
    AND b."Status"::text NOT IN ('cancelada', 'descartada', 'descartadapagada')
    AND COALESCE(b."Incasol_deposit", 0) > 0

  UNION ALL

  -- Altas Incasol B2B (reservas de grupo), una fila por reserva con la fianza total
  -- Los datos del piso solo si todas las plazas estan en el mismo piso, el recurso solo si es unico
  SELECT
    'B' || g.id,
    CASE WHEN COUNT(DISTINCT r."Code") = 1 THEN MIN(r."Code") END,
    COALESCE(CASE WHEN COUNT(DISTINCT COALESCE(r."Street", f."Street")) = 1 THEN MIN(COALESCE(r."Street", f."Street")) END, MIN(bu."Address")),
    CASE WHEN COUNT(DISTINCT COALESCE(f."Address", r."Address")) = 1 THEN MIN(COALESCE(f."Address", r."Address")) END,
    MIN(bu."Zip"),
    MIN(l."Name"),
    CASE WHEN COUNT(DISTINCT COALESCE(r."Registry_code", f."Registry_code", bu."Cadastral_ref")) = 1 THEN MIN(COALESCE(r."Registry_code", f."Registry_code", bu."Cadastral_ref")) END,
    CASE WHEN COUNT(DISTINCT COALESCE(r."Area_woc", f."Area_woc")) = 1 THEN MIN(COALESCE(r."Area_woc", f."Area_woc")) END,
    CASE WHEN COUNT(DISTINCT COALESCE(r."Occupancy_certificate", f."Occupancy_certificate")) = 1 THEN MIN(COALESCE(r."Occupancy_certificate", f."Occupancy_certificate")) END,
    MIN(c."Name"),
    MIN(c."Document"),
    CASE WHEN COUNT(DISTINCT p."Name") = 1 THEN MIN(p."Name") END,
    CASE WHEN COUNT(DISTINCT p."Document") = 1 THEN MIN(p."Document") END,
    CASE WHEN COUNT(DISTINCT CONCAT_WS(', ', p."Address", p."Zip", p."City")) = 1 THEN MIN(CONCAT_WS(', ', p."Address", p."Zip", p."City")) END,
    g."Incasol_deposit",
    g."Contract_signed",
    1000000 + g.id
  FROM "Booking"."Booking_group" g
    LEFT JOIN "Booking"."Booking_group_rooms" gr ON gr."Booking_id" = g.id
    LEFT JOIN "Resource"."Resource" r ON r.id = gr."Resource_id"
    LEFT JOIN "Resource"."Resource" f ON f.id = r."Flat_id"
    INNER JOIN "Building"."Building" bu ON bu.id = COALESCE(r."Building_id", g."Building_id")
    LEFT JOIN "Geo"."District" d ON d.id = bu."District_id"
    LEFT JOIN "Geo"."Location" l ON l.id = d."Location_id"
    LEFT JOIN "Customer"."Customer" c ON c.id = g."Payer_id"
    LEFT JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
  WHERE g."Contract_signed" >= %(fdesde)s AND g."Contract_signed" < %(fhasta)s
    AND g."Status"::text NOT IN ('cancelada', 'descartada', 'descartadapagada')
    AND COALESCE(g."Incasol_deposit", 0) > 0
  GROUP BY g.id
)
SELECT
  -- Separa la calle del numero (ultimo numero de "Street"), si no se puede queda todo en la calle
  TRIM(REGEXP_REPLACE(a."Street", '[\s,]+(n[ºo°]\.?\s*)?\d[\d\-]*[A-Za-z]?\s*$', '', 'i')) AS "Street",
  SUBSTRING(a."Street" FROM '(\d[\d\-]*[A-Za-z]?)\s*$')                                  AS "Number",
  NULL                                                                                   AS "Stair",
  a."Address",
  a."Id",
  a."Resource",
  a."Zip",
  a."City",
  a."Cadastral_ref",
  a."Area",
  a."Occupancy_certificate",
  a."Customer_name",
  a."Customer_document",
  a."Owner_name",
  a."Owner_document",
  a."Owner_address",
  a."Incasol_deposit",
  a."Contract_signed"
FROM altas a
-- Primero las B2C, luego las B2B (+1000000), cada bloque por nº de reserva
ORDER BY a."Sort_id"
;
