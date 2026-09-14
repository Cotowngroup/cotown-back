-- Calcula la fianza legal (Incasol) del grupo
-- BEFORE UPDATE, despues de validar y calcular el deposito
DECLARE

  legal_deposit NUMERIC;
  barcelona BOOLEAN;

BEGIN

  -- Already calculated or prices not calculated yet
  IF NEW."Incasol_deposit" IS NOT NULL
     OR NOT EXISTS (SELECT 1 FROM "Booking"."Booking_group_price" WHERE "Booking_id" = NEW.id) THEN
    RETURN NEW;
  END IF;

  -- Base per room: rent, plus utility, furniture and expenses when limited
  IF NEW."Book_type" = 'limitado' THEN
    legal_deposit := COALESCE(NEW."Rent", 0) + COALESCE(NEW."Limit", 0) + COALESCE(NEW."Furniture", 0) + COALESCE(NEW."Expenses", 0);
  ELSE
    legal_deposit := COALESCE(NEW."Rent", 0);
  END IF;

  -- Whole flats: two months, prorated over the stay
  IF NEW."Full_flat" THEN
    legal_deposit := ROUND(LEAST(legal_deposit * (NEW."Date_to" - NEW."Date_from" + 1) / 180, 2 * legal_deposit), 2);
  END IF;

  -- Location
  SELECT d."Location_id" = 1
  INTO barcelona
  FROM "Building"."Building" bu
    INNER JOIN "Geo"."District" d ON d.id = bu."District_id"
  WHERE bu.id = NEW."Building_id";

  -- Only in Barcelona, and only with a deposit
  IF NOT COALESCE(barcelona, FALSE) OR NEW."Deposit" IS NULL THEN
    legal_deposit := 0;
  END IF;

  -- The deposit (per room) always includes the legal deposit
  IF NEW."Deposit" < legal_deposit THEN
    NEW."Deposit" := legal_deposit;
  END IF;
  NEW."Incasol_deposit" := legal_deposit * COALESCE(NEW."Rooms", 0);

  RETURN NEW;

END;
