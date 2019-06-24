DROP EXTENSION IF EXISTS "uuid-ossp";
CREATE EXTENSION "uuid-ossp";

DROP SCHEMA IF EXISTS "sourcing" CASCADE;
CREATE SCHEMA "sourcing";

DROP TABLE IF EXISTS "sourcing"."eventstore";
DROP SEQUENCE IF EXISTS "sourcing"."eventstore_id_seq";

CREATE SEQUENCE IF NOT EXISTS eventstore_id_seq
    INCREMENT BY 1
    MINVALUE 1
    NO MAXVALUE
    START WITH 1;

CREATE TABLE sourcing.eventstore ( 
	"id" BIGINT DEFAULT nextval('eventstore_id_seq'::regclass) NOT NULL,
    "user_id" integer NOT NULL,
	"event" CHARACTER VARYING( 2044 ) NOT NULL,
	"type" CHARACTER VARYING( 2044 ),
	"data" jsonb NOT NULL DEFAULT '{}',
	"timestamp" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
	"uuid" UUID,
	PRIMARY KEY ( "id" ) 
);

ALTER TABLE ONLY sourcing.eventstore
    ADD CONSTRAINT eventstore_user FOREIGN KEY (user_id) REFERENCES public.user(id) MATCH FULL ON UPDATE CASCADE ON DELETE NO ACTION;

CREATE OR REPLACE FUNCTION sourcing."on_event"( ) RETURNS TRIGGER AS
$function$
DECLARE
    id BIGINT;
    data_type CHARACTER VARYING(2044);
    query_1 TEXT := '';
    query_2 TEXT := '';
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
                CASE WHEN (NEW.data ? rec.col_name) = TRUE THEN
                    query_1 = query_1 || ', ' || quote_ident(rec.col_name);
                    CASE rec.col_type
                        WHEN 'USER-DEFINED' THEN
                            query_2 = query_2 || ', CAST('|| quote_literal((NEW.data->>rec.col_name)) || ' AS ' ||
                                quote_ident(rec.udt_schema) || '.' || quote_ident(rec.udt_name) || ' )';
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
            INSERT INTO "sourcing"."eventstore" ("event", "type", "uuid", "timestamp", "user_id") (
                SELECT 'delete' AS "event", "type" , "uuid", 
                       NEW.timestamp AS "timestamp",
                       NEW.user_id AS "user_id"
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
                     ("event", "type", "uuid", "data", "timestamp", "user_id") (
		                SELECT "event", 
                               "type", 
                               "uuid", 
                               "data", '
                               || quote_literal(NEW.timestamp) || ' AS "timestamp", '
                               || quote_literal(NEW.user_id) || ' AS "user_id" 
		                FROM "sourcing"."eventstore"
    		            WHERE ' || LEFT(query_1, -4) ||
		               'ORDER BY "eventstore"."id" ASC)';
            INSERT INTO "sourcing"."eventstore" ("event", "data", "timestamp", "user_id") 
                   VALUES ('rollback-end', NEW.data, NEW.timestamp, NEW.user_id);
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
