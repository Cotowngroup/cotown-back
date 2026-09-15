-- Inicializa la solicitud
DECLARE

  booking_fee_amount INTEGER;
  year INTEGER;

  promotion RECORD;

BEGIN

  -- Status por defecto
  IF NEW."Status" IS NULL THEN
    NEW."Status" := 'solicitud';
  END IF;

  -- IVA por defecto según edificio
  SELECT COALESCE(bt."Tax_id", 2)
  INTO NEW."Tax_id"
  FROM "Building"."Building" b
  INNER JOIN "Building"."Building_type" bt ON bt.id = b."Building_type_id"
  WHERE b.id = NEW."Building_id";

  -- Promoción
  -- Web: la envía el backend, la misma que se muestra en el resumen de la reserva (conoce el segmento).
  -- Alta manual sin promoción: se aplica la mejor que no depende del recurso (régimen 'ambos').
  -- Las promociones de régimen libre o limitado se asignan a mano, junto con el recurso.
  IF NEW."Promotion_id" IS NOT NULL THEN

    SELECT *
    INTO promotion
    FROM "Billing"."Promotion"
    WHERE id = NEW."Promotion_id";

  ELSE

    SELECT *
    INTO promotion
    FROM "Billing"."Promotion" p
    WHERE p."Date_from" <= NEW."Date_to"
      AND p."Date_to" >= NEW."Date_from"
      AND p."Active_from" <= CURRENT_DATE
      AND p."Active_to" >= CURRENT_DATE
      -- Régimen: solo las que valen para cualquier recurso
      AND COALESCE(p."Limit_type", 'ambos') = 'ambos'
      -- Edificio: si no hay filas para la promo -> aplica a todos.
      AND (
        NOT EXISTS (
          SELECT 1
          FROM "Billing"."Promotion_building" pb0
          WHERE pb0."Promotion_id" = p.id
        )
        OR EXISTS (
          SELECT 1
          FROM "Billing"."Promotion_building" pb
          WHERE pb."Promotion_id" = p.id
            AND pb."Building_id"  = NEW."Building_id"
        )
      )
      -- Tipos de piso/plaza: Si no hay filas -> aplica a todos.
      AND (
        NOT EXISTS (
          SELECT 1
          FROM "Billing"."Promotion_place" pp0
          WHERE pp0."Promotion_id" = p.id
        )
        OR EXISTS (
          SELECT 1
          FROM "Billing"."Promotion_place" pp
          WHERE pp."Promotion_id" = p.id
            AND (pp."Flat_type_id"  IS NULL OR pp."Flat_type_id"  = NEW."Flat_type_id")
            AND (pp."Place_type_id" IS NULL OR pp."Place_type_id" = NEW."Place_type_id")
        )
      )
    ORDER BY p."Value_rent_pct" ASC NULLS LAST, p."Value_fee_pct" ASC NULLS LAST, id DESC
    LIMIT 1;
    NEW."Promotion_id" = promotion.id;

  END IF;

  -- Calcula el membership fee si está vacío
  IF NEW."Booking_fee_calc" IS NULL THEN

    -- Year
    year := EXTRACT(YEAR FROM NEW."Date_from");
    IF EXTRACT(MONTH FROM NEW."Date_from") > 8 THEN
      year := year + 1;
    END IF; 

    -- Obtiene el valor del membership fee
    SELECT COALESCE("Booking_fee", 0)
    INTO booking_fee_amount
    FROM "Billing"."Pricing_detail" pd
    WHERE pd."Building_id" = NEW."Building_id"
      AND pd."Flat_type_id" = NEW."Flat_type_id"
      AND (pd."Place_type_id" = NEW."Place_type_id" OR NEW."Place_type_id" IS NULL)
      AND pd."Year" = year
    LIMIT 1;
    NEW."Booking_fee_calc" := booking_fee_amount;

    -- Asigna el valor obtenido con posible promoción
    IF NEW."Booking_fee" IS NULL THEN
      IF promotion."Value_fee_pct" IS NOT NULL THEN
        booking_fee_amount := booking_fee_amount * (1 + promotion."Value_fee_pct" / 100);
        NEW."Booking_discount_type_id" := 1;
      ELSE
        IF promotion."Value_fee" IS NOT NULL THEN
          booking_fee_amount := booking_fee_amount + promotion."Value_fee";
          NEW."Booking_discount_type_id" := 1;
        END IF;
      END IF;
      NEW."Booking_fee" := booking_fee_amount;
    END IF;

  END IF;

  -- Return
  RETURN NEW;

END;