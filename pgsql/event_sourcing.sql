-- DROP EXTENSION IF EXISTS "uuid-ossp";
--CREATE EXTENSION "uuid-ossp";

DROP SCHEMA IF EXISTS "sourcing" CASCADE;
CREATE SCHEMA "sourcing";

DROP TABLE IF EXISTS "sourcing"."eventstore";
DROP SEQUENCE IF EXISTS "sourcing"."eventstore_id_seq";

CREATE SEQUENCE IF NOT EXISTS sourcing.eventstore_id_seq
    INCREMENT BY 1
    MINVALUE 1
    NO MAXVALUE
    START WITH 1;

CREATE TABLE sourcing.eventstore ( 
	"id" BIGINT DEFAULT nextval('sourcing.eventstore_id_seq'::regclass) NOT NULL,
	"event" CHARACTER VARYING( 2044 ) NOT NULL,
	"type" CHARACTER VARYING( 2044 ),
	"data" jsonb NOT NULL DEFAULT '{}',
	"timestamp" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
	"uuid" UUID,
	PRIMARY KEY ( "id" ) 
);

-- LAB_MMDDYYYY_XXX --
CREATE OR REPLACE FUNCTION public.create_synthesis_hid ( synth_machine_id UUID, ts TIMESTAMP WITHOUT TIME ZONE) 
RETURNS CHARACTER VARYING(16) AS $synth_hid$
DECLARE
    synth_hid TEXT := '';
BEGIN
    IF (SELECT EXISTS(SELECT * FROM public.synthesis_machine AS sm WHERE sm.uuid = synth_machine_id)) THEN
        synth_hid = (SELECT short_name FROM public.lab AS lab 
                     INNER JOIN public.synthesis_machine AS sm 
                     ON sm.lab_id = lab.uuid 
                     WHERE sm.uuid = synth_machine_id) || '_';
        synth_hid = synth_hid || (SELECT EXTRACT(MONTH FROM ts)) || '-' || 
                                 (SELECT EXTRACT(DAY FROM ts))   || '-' ||
                                 (SELECT EXTRACT(YEAR FROM ts));
        synth_hid = synth_hid || '_' ||
        (SELECT COUNT(*) FROM public.synthesis AS syn 
        INNER JOIN public.synthesis_machine AS sm ON syn.machine_id = sm.uuid 
        INNER JOIN public.lab AS lab ON sm.lab_id = lab.uuid 
        WHERE syn.created_on > current_date - interval '1 day'
        AND sm.uuid = synth_machine_id);
    ELSE
        RAISE 'machine_id does not exists!';
    END IF;
    RETURN synth_hid;
END;
$synth_hid$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION sourcing."on_event"( ) RETURNS TRIGGER AS
$function$
DECLARE
    id BIGINT;
    data_type CHARACTER VARYING(2044);
    query_1 TEXT := '';
    query_2 TEXT := '';
    hid CHARACTER VARYING(16) := '';
    rec record;
    count INT := 1;
BEGIN
    CASE WHEN NEW.timestamp IS NULL THEN
        NEW.timestamp := now();
    ELSE
    END CASE;

    CASE NEW.event
        -- DATA ADDITION --
        WHEN 'create' THEN
            CASE WHEN NEW.uuid IS NULL THEN
                NEW.uuid := uuid_generate_v4();
            ELSE
            END CASE;

            FOR rec in (
                SELECT "columns"."column_name" AS "col_name",
                       "columns"."data_type" AS "col_type",
                       "columns"."udt_name" AS "udt_name", 
                       "columns"."udt_schema" AS "udt_schema"
                    FROM "information_schema"."columns"
                    WHERE "table_schema" = 'public' AND "table_name" = NEW.type )
            LOOP
                -- if column name is in data
                CASE WHEN (NEW.data ? rec.col_name) = TRUE THEN
                    query_1 = query_1 || ', ' || quote_ident(rec.col_name);
                    CASE rec.col_type
                        WHEN 'USER-DEFINED' THEN
                            query_2 = query_2 || ', CAST('|| quote_literal((NEW.data->>rec.col_name)) || ' AS ' ||
                                quote_ident(rec.udt_schema) || '.' || quote_ident(rec.udt_name) || ' )';

                        -- for now, the only array we have are of float8 type
                        WHEN 'ARRAY' THEN
                            query_2 = query_2 || ', CAST( '|| quote_literal((SELECT array_agg(e::text) FROM 
                                jsonb_array_elements(NEW.data->rec.col_name) e)::TEXT) || ' AS  FLOAT8[] )';
                        ELSE
                            query_2 = query_2 || ', CAST(' || quote_literal((NEW.data->>rec.col_name)) || ' AS ' ||
                                rec.col_type || ' )';
                    END CASE;
                ELSE
                    CASE WHEN rec.col_name = 'updated_on' OR  rec.col_name = 'created_on' THEN
                        query_1 = query_1 || ', ' || quote_ident(rec.col_name);
                        query_2 = query_2 || ',  CAST('|| quote_literal(NEW.timestamp) || ' AS ' || rec.col_type || ')';
                    ELSE
                    END CASE;
                    CASE WHEN NEW.type = 'synthesis' AND rec.col_name = 'hid' THEN
                        hid = (SELECT public.create_synthesis_hid((NEW.data->>'machine_id')::uuid, NEW.timestamp));
                        query_1 = query_1 || ', ' || quote_ident(rec.col_name);
                        query_2 = query_2 || ', CAST(' || quote_literal(hid) || ' AS ' || rec.col_type || ')';
                        NEW.data = jsonb_insert(NEW.data, '{hid}', quote_ident((hid::text))::jsonb);
                    ELSE
                    END CASE;
                END CASE;
            END LOOP;
            EXECUTE 'INSERT INTO public.' || quote_ident(NEW.type) 
                || '("uuid"' || query_1 || ')' 
                || ' VALUES (' || quote_literal(NEW.uuid) || query_2 || ') RETURNING "id"'
            INTO id;
            -- ADDING THE ID IN CASE OF ROLLBACK
            NEW.data := jsonb_set(NEW.data, '{id}'::TEXT[], to_jsonb(id::INT));

        -- DATA UPDATE --
        WHEN 'update' THEN
            FOR rec in (
                SELECT "columns"."column_name" AS "col_name",
                       "columns"."data_type" AS "col_type",
                       "columns"."udt_name" AS "udt_name",
                       "columns"."udt_schema" AS "udt_schema"
                    FROM "information_schema"."columns"
                    WHERE "table_schema" = 'public' AND "table_name" = NEW.type )
            LOOP
                CASE WHEN (NEW.data ? rec.col_name) = TRUE THEN
                    CASE
                        WHEN rec.col_type='USER-DEFINED' THEN
                            query_1 = query_1 || ', ' || quote_ident(rec.col_name) || 
                                ' = CAST(' || quote_literal((NEW.data->>rec.col_name)) || ' AS ' ||
                                    quote_ident(rec.udt_schema) || '.' || quote_ident(rec.udt_name) || ' )';
                        -- Add here things about jsonb merging select json_a ::jsonb || json_b ::jsonb should do the job
                        WHEN rec.col_type='jsonb' THEN
                            query_1 = query_1 || ', ' || quote_ident(rec.col_name) || 
                                ' = ( SELECT '|| quote_ident(rec.col_name) || ' FROM "public".' || quote_ident(NEW.type) || 
                                ' WHERE ' || quote_ident(NEW.type) || '.uuid = ' || quote_literal(NEW.uuid) || ') || CAST( ' || 
                                quote_literal((NEW.data->>rec.col_name)) || ' AS ' || quote_ident(rec.col_type) || ')';
                        ELSE
                            query_1 = query_1 || ', ' || quote_ident(rec.col_name) || 
                                ' = CAST(' || quote_literal((NEW.data->>rec.col_name)) || ' AS ' || rec.col_type || ')';
                    END CASE;
                ELSE
                    CASE rec.col_name
                        WHEN 'updated_on' THEN
                            query_1 = query_1 || ', updated_on = CAST(' || quote_literal(NEW.timestamp) || ' AS ' || rec.col_type || ')';
                        ELSE
                    END CASE;
                END CASE;
            END LOOP;

            EXECUTE 'UPDATE public.' || quote_ident(NEW.type) || ' SET ' || RIGHT(query_1, -2) 
                || ' WHERE "uuid" = ' || quote_literal(NEW.uuid);

            GET DIAGNOSTICS count = ROW_COUNT;
        
        -- DATA DELETION -- 
        WHEN 'delete' THEN
            EXECUTE 'DELETE FROM "public".' || quote_ident(NEW.type) 
                || ' WHERE "uuid" = '|| quote_literal(NEW.uuid);
            GET DIAGNOSTICS count = ROW_COUNT;
        -- ROLLBACK MANOEUVER --
        WHEN 'rollback-start' THEN
        WHEN 'rollback-end' THEN
        WHEN 'rollback' THEN
            -- Remove everything that has not been removed yet
            INSERT INTO "sourcing"."eventstore" ("event", "type", "uuid", "timestamp") (
                SELECT 'delete' AS "event", "type" , "uuid", 
                       NEW.timestamp AS "timestamp"
                    FROM "sourcing"."eventstore" 
                    GROUP BY "uuid", "type" 
                    HAVING NOT (array_agg("event") @> '{delete}' OR "uuid" IS NULL)
                    ORDER BY min("eventstore"."id") DESC
            );
            CASE WHEN (NEW.data ? 'before') THEN
                query_1 = '"eventstore"."timestamp" < ' || quote_literal((NEW.data->>'before')) ||' ::TIMESTAMP WITHOUT TIME ZONE AND ';
            ELSE
            END CASE;
            CASE WHEN query_1 = '' THEN
                RAISE invalid_parameter_value USING MESSAGE = 'No criterion for the rollback was selected.';
            ELSE
            END CASE;
            EXECUTE 'INSERT INTO "sourcing"."eventstore" 
                     ("event", "type", "uuid", "data", "timestamp") (
		                SELECT "event", 
                               "type", 
                               "uuid", 
                               "data", '
                               || quote_literal(NEW.timestamp) || ' AS "timestamp"
		                FROM "sourcing"."eventstore"
    		            WHERE ' || LEFT(query_1, -4) ||
		               'ORDER BY "eventstore"."id" ASC)';
            INSERT INTO "sourcing"."eventstore" ("event", "data", "timestamp") 
                   VALUES ('rollback-end', NEW.data, NEW.timestamp);
            NEW.event := 'rollback-start';
        ELSE
            RAISE unique_violation USING MESSAGE = 'Invalid event type '|| quote_literal(NEW.event);
        END CASE;

        IF count = 0 THEN
            RAISE unique_violation USING MESSAGE = 'No item matches the provided uuid ' || quote_literal(NEW.uuid);
        END IF;

    RETURN NEW;
END;
$function$
LANGUAGE plpgsql;


CREATE TRIGGER on_event_insert
    BEFORE INSERT
    ON "sourcing"."eventstore"
    FOR EACH ROW
        EXECUTE PROCEDURE "sourcing"."on_event"();
