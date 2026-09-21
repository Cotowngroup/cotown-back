-- Bajas Incasol B2C (reservas individuales con fianza legal), por fecha de salida
SELECT
  b.id::text                                        AS "Id",
  r."Code"                                          AS "Resource",
  NULL                                              AS "Incasol_registry", -- TODO: b."Incasol_registry" cuando exista el campo en CORE
  COALESCE(b."Check_out", b."Date_to")              AS "Date_to",
  CONCAT_WS(', ', COALESCE(r."Street", f."Street"), COALESCE(f."Address", r."Address"), bu."Zip", l."Name") AS "Address",
  b."Incasol_deposit"                               AS "Incasol_deposit",
  b."Incasol_type"::text                            AS "Incasol_type",
  c."Name"                                          AS "Customer_name",
  b.id                                              AS "Sort_id"
FROM "Booking"."Booking" b
  INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
  LEFT JOIN "Resource"."Resource" f ON f.id = r."Flat_id"
  INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id"
  LEFT JOIN "Geo"."District" d ON d.id = bu."District_id"
  LEFT JOIN "Geo"."Location" l ON l.id = d."Location_id"
  LEFT JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
WHERE COALESCE(b."Check_out", b."Date_to") >= %(fdesde)s AND COALESCE(b."Check_out", b."Date_to") < %(fhasta)s
  AND b."Contract_signed" IS NOT NULL
  AND b."Status"::text NOT IN ('cancelada', 'descartada', 'descartadapagada')
  AND COALESCE(b."Incasol_deposit", 0) > 0

UNION ALL

-- Bajas Incasol B2B (reservas de grupo), una fila por reserva con la fianza total
-- La direccion del piso solo si todas las plazas estan en el mismo piso, el recurso es el piso (o pisos) y el nº de plazas
SELECT
  'B' || g.id,
  COALESCE(STRING_AGG(DISTINCT COALESCE(f."Code", r."Code"), ', '), MIN(bu."Code")) || ' (' || COALESCE(g."Rooms", COUNT(gr.id)) || ' plazas)',
  NULL, -- TODO: g."Incasol_registry" cuando exista el campo en CORE
  g."Date_to",
  COALESCE(
    CASE WHEN COUNT(DISTINCT CONCAT_WS(', ', COALESCE(r."Street", f."Street"), COALESCE(f."Address", r."Address"), bu."Zip", l."Name")) = 1 THEN MIN(CONCAT_WS(', ', COALESCE(r."Street", f."Street"), COALESCE(f."Address", r."Address"), bu."Zip", l."Name")) END,
    CONCAT_WS(', ', MIN(bu."Address"), MIN(bu."Zip"), MIN(l."Name"))
  ),
  g."Incasol_deposit",
  NULL,
  MIN(c."Name"),
  1000000 + g.id
FROM "Booking"."Booking_group" g
  LEFT JOIN "Booking"."Booking_group_rooms" gr ON gr."Booking_id" = g.id
  LEFT JOIN "Resource"."Resource" r ON r.id = gr."Resource_id"
  LEFT JOIN "Resource"."Resource" f ON f.id = r."Flat_id"
  INNER JOIN "Building"."Building" bu ON bu.id = COALESCE(r."Building_id", g."Building_id")
  LEFT JOIN "Geo"."District" d ON d.id = bu."District_id"
  LEFT JOIN "Geo"."Location" l ON l.id = d."Location_id"
  LEFT JOIN "Customer"."Customer" c ON c.id = g."Payer_id"
WHERE g."Date_to" >= %(fdesde)s AND g."Date_to" < %(fhasta)s
  AND g."Contract_signed" IS NOT NULL
  AND g."Status"::text NOT IN ('cancelada', 'descartada', 'descartadapagada')
  AND COALESCE(g."Incasol_deposit", 0) > 0
GROUP BY g.id

-- Primero las B2C, luego las B2B (+1000000), cada bloque por nº de reserva
ORDER BY "Sort_id"
;
