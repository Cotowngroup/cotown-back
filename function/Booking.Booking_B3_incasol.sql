-- Calcula la fianza legal (Incasol)
-- BEFORE UPDATE, despues de calcular los precios
DECLARE

  legal_deposit NUMERIC;
  resource_type VARCHAR;
  barcelona BOOLEAN;

BEGIN

  -- Already calculated, no resource or prices not calculated yet
  IF NEW."Incasol_deposit" IS NOT NULL
     OR NEW."Resource_id" IS NULL
     OR NOT EXISTS (SELECT 1 FROM "Booking"."Booking_price" WHERE "Booking_id" = NEW.id) THEN
    RETURN NEW;
  END IF;

  -- Base: rent, plus utility, furniture and expenses when limited
  IF NEW."Book_type" = 'limitado' THEN
    legal_deposit := COALESCE(NEW."Rent", 0) + COALESCE(NEW."Limit", 0) + COALESCE(NEW."Furniture", 0) + COALESCE(NEW."Expenses", 0);
  ELSE
    legal_deposit := COALESCE(NEW."Rent", 0);
  END IF;

  -- Resource type and location
  SELECT d."Location_id" = 1, r."Resource_type"
  INTO barcelona, resource_type
  FROM "Resource"."Resource" r
    INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id"
    INNER JOIN "Geo"."District" d ON d.id = bu."District_id"
  WHERE r.id = NEW."Resource_id";

  -- Whole flats booked for leisure: two months, prorated over the stay
  IF resource_type = 'piso' AND NEW."Book_type" = 'recreativo' THEN
    legal_deposit := ROUND(LEAST(legal_deposit * (NEW."Date_to" - NEW."Date_from" + 1) / 180, 2 * legal_deposit), 2);
  END IF;

  -- Only in Barcelona, and only with a deposit
  IF NOT COALESCE(barcelona, FALSE) OR NEW."Deposit" IS NULL THEN
    legal_deposit := 0;
  END IF;

  -- Legal deposit as calculated, the deposit is left untouched
  NEW."Incasol_deposit" := legal_deposit;

  RETURN NEW;

END;
