
  drop schema if exists "sourcing" cascade;
create schema           "sourcing";

drop table    if exists sourcing.eventstore;
drop sequence if exists sourcing.eventstore_id_seq;

create sequence if not exists 
       sourcing.eventstore_id_seq
       increment by 1
           minvalue 1
        no maxvalue
         start with 1;

create table sourcing.eventstore (
    "id"    bigint default nextval('sourcing.eventstore_id_seq'::regclass) not null,
    "event" character varying(2044)                                        not null,
    "type"  character varying(2044),
    "data"  jsonb    default '{}'                                                      not null,
    "timestamp" timestamp without time zone default now()::timestamp without time zone not null,
    "uuid" uuid,
    primary key ( "id" )
);


-- create a human readable id for the synthesis
create or replace function public.create_synthesis_hid ( synth_machine_id uuid, ts timestamp without time zone)
returns character varying(16) as $synth_hid$
declare
    synth_hid text := '';
    owner_lab_id uuid;
    rec record;
begin
    if (select exists(select synthesis_machine_id 
                        from public.synthesis_machine as sm 
                       where sm.synthesis_machine_id = synth_machine_id
        )) then

        -- lab owning the machine
        owner_lab_id = (select lab.lab_id from public.lab as lab 
                          join public.synthesis_machine as sm using(lab_id)
                         where sm.synthesis_machine_id = synth_machine_id);

        synth_hid = format('%s_%s_%s',
        (select lab.short_name from public.lab where lab_id = owner_lab_id),
        (select to_char(ts, 'YYYY-MM-DD')),
        (select  count(*)
           from public.synthesis as syn
left outer join public.synthesis_machine as sm using(synthesis_machine_id)
           join public.lab as lab using(lab_id)
          where lab.lab_id = owner_lab_id
            and syn.created_on > current_date - interval '1 day'));
        return synth_hid;
    else
        raise using message = format('could not find machine with the provided id %s', synth_machine_id);
    end if;
end;
$synth_hid$
language plpgsql;


-- on_create_query
--
-- builds an insert query from a record
create or replace function sourcing.on_create_query(new record)
returns text as $query_txt$
declare
    q1 text := '';
    q2 text := '';
    hid character varying(16) := '';
    rec record;
begin
    for rec in (
        select columns.column_name as col_name,
                 columns.data_type as col_type,
                  columns.udt_name as udt_name,
                columns.udt_schema as udt_schema
         from information_schema.columns
        where table_schema = 'public' and table_name = new.type 
    )
    loop
        continue when rec.col_name = format('%s_id', rec.col_type);
        if new.data ? rec.col_name = true then
            q1 = q1 || format(', %I', rec.col_name);
            case rec.col_type
            when 'USER-DEFINED' then
                q2 = q2 || format(', cast( %L as %I.%I )', 
                      new.data->>rec.col_name, rec.udt_schema, rec.udt_name);
            when 'ARRAY' then
                -- the current schema has only array of float8
                q2 = q2 || format(', cast( %L as float8[])',
                                  (select array_agg(arr::text)
                                     from jsonb_array_elements((new.data->>rec.col_name)::jsonb) arr)::text);
            when 'character varying' then
                q2 = q2 || format(', cast( %L as character varying(%s))',
                                  new.data->>rec.col_name,
                                  (select character_maximum_length 
                                     from information_schema.columns 
                                    where table_schema = 'public'
                                      and   table_name = new.type
                                      and  column_name = rec.col_name));
            else
                q2 = q2 || format(', cast( %L as %s )',
                                  new.data->>rec.col_name,
                                  rec.col_type);
            end case;
        else
           if rec.col_name = 'created_on' or rec.col_name = 'updated_on' then
                q1 = q1 || format(', %I', rec.col_name);
                q2 = q2 || format(', cast( %L as timestamp without time zone )', new.timestamp);
           elsif new.type = 'synthesis' and rec.col_name = 'hid' then
                -- synthesis has a special field - hid that is a human id generated automatically
                q1 = q1 || format(', %I', rec.col_name);
                hid = (select public.create_synthesis_hid(
                        (new.data->>'synthesis_machine_id')::uuid,
                         new.timestamp));
                q2 = q2 || format(', cast( %L as character varying(%s) )',
                                  hid,
                                  (select character_maximum_length
                                     from information_schema.columns
                                    where table_schema = 'public'
                                      and   table_name = new.type
                                      and  column_name = rec.col_name));
                new.data = jsonb_insert(new.data, '{hid}', quote_ident((hid::text))::jsonb);
            end if;
        end if;
    end loop;
    
    return format('insert into public.%I ("%s_id" %s) values (%L %s) returning "%s_id"',
                  new.type, new.type, q1, new.uuid, q2, new.type);
end;
$query_txt$
language plpgsql;


create or replace function sourcing.on_update_query(new record)
returns text as $query_txt$
declare
    q1 text := '';
    rec record;
begin
    if new.uuid is null then
        raise null_value_not_allowed using message='No uuid has been provided';
    end if;
    for rec in (
        select columns.column_name as col_name,
                 columns.data_type as col_type,
                  columns.udt_name as udt_name,
                columns.udt_schema as udt_schema
          from information_schema.columns
         where table_schema = 'public' and table_name = new.type
    )
    loop
        continue when rec.col_name = format('%s_id', rec.col_type);
        if new.data ? rec.col_name = true then
            case
            when rec.col_type = 'user-defined' then
                q1 = q1 || format(', %I cast( %L as %I.%I )',
                                  rec.col_name,
                                  new.data->>rec.col_name,
                                  rec.udt_schema,
                                  rec.udt_name);
            when rec.col_type = 'jsonb' then
                -- Does an aggreagation of the two jsonb. Last key wins.
                q1 = q1 || format(', %I = ( select %I from public.%I 
                                             where %I.%s_id=%L ) || cast( %L as jsonb )',
                                    rec.col_name, rec.col_name, new.type, new.type, 
                                    new.type, new.uuid, new.data->>rec.col_name);
            when rec.col_type = 'ARRAY' then
                q1 = q1 || format(', %I = cast( %L as float8[] )',
                                  rec.col_name, 
                                  (select array_agg(arr::text)
                                     from jsonb_array_elements((new.data->>rec.col_name)::jsonb) arr)::text);
            when rec.col_type = 'character varying' then
                q1 = q1 || format(', %I = cast( %L as character varying(%s) )',
                                  rec.col_name,
                                  new.data->>rec.col_name,
                                  (select character_maximum_length
                                     from information_schema.columns
                                    where table_schema = 'public'
                                      and   table_name = new.type
                                      and  column_name = rec.col_name));
            else
                q1 = q1 || format(', %I = cast( %L as %s )',
                                  rec.col_name, new.data->>rec.col_name, rec.col_type);
            end case;
        else
            if rec.col_name = 'updated_on' then
                q1 = q1 || format(', updated_on = cast( %L as timestamp without time zone )',
                                  new.timestamp);
            end if;
        end if;
    end loop;
    return format('update public.%I set %s where "%s_id" = %L',
                  new.type, right(q1, -2), new.type, new.uuid);
end;
$query_txt$
language plpgsql;


create or replace function sourcing.on_delete_query(new record)
returns text as $query_txt$
begin
    if new.uuid is null then
        raise null_value_not_allowed using message='No uuid have been provided';
    end if;
    return format('delete from public.%I where "%s_id"=%L',
                  new.type, new.type, new.uuid);

end;
$query_txt$
language plpgsql;


create or replace function sourcing.on_rollback_query(new record)
returns text as $query_txt$
declare
    q1 text := '';
begin

    -- removing everything that has not been removed yet
    insert into sourcing.eventstore 
       ("event", "type", "uuid", "timestamp") (
            select 'delete' as "event",
                   "type",
                   "uuid", 
                   new.timestamp as "timestamp"
              from sourcing.eventstore 
          group by "uuid", "type" 
            having not (array_agg("event") @> '{delete}' 
                    or "uuid" is null)
          order by min("eventstore"."id") desc
    );

    if (new.data ? 'before') then
        q1 = format('eventstore.timestamp < %L ::timestamp without time zone and ',
                    new.data->>'before');
    end if;
    if (new.data ? 'after') then
        q1 = q1 || format('eventstore.timestamp > %L ::timestamp without time zone and ',
                          new.data->>'after');
    end if;

    if q1 = '' then
        raise invalid_parameter_value using message = 'No criterion were provided for the rollback';
    end if;
    return format('insert into sourcing.eventstore 
                     ("event", "type", "uuid", "data", "timestamp") (
		                select "event", 
                               "type", 
                               "uuid", 
                               "data", 
                               %L  as "timestamp"
		                  from "sourcing"."eventstore"
    		             where %s
		              order by "eventstore"."timestamp" asc)',
                new.timestamp, left(q1, -4));
end;
$query_txt$
language plpgsql;


--
-- Trigger function that binds everything together
--
create or replace function sourcing."on_event"( ) 
returns trigger as $function$
declare
    count INT := 1;
begin
    if new.timestamp is null then
        new.timestamp := now()::timestamp without time zone;
    end if;

    case new.event
    when 'create' then
        if new.uuid is null then
            new.uuid := uuid_generate_v4();
        end if;
        execute (select sourcing.on_create_query(new));
    when 'update' then
        execute (select sourcing.on_update_query(new));
        get diagnostics count = ROW_COUNT;
    when 'delete' then
        execute (select sourcing.on_delete_query(new));
        get diagnostics count = ROW_COUNT;
    when 'rollback-begin' then
    when 'rollback-end' then
    when 'rollback' then
        execute (select sourcing.on_rollback_query(new));
        insert into sourcing.eventstore 
            ("event", "data", "timestamp")
     values ('rollback-end', new.data, now()::timestamp without time zone);
        new.event := 'rollback-begin';
    else
        raise unique_violation using message = format('Invalid event type: %L', new.event);
    end case;

    if count = 0 then
        raise no_data_found using message = format('No item matches the uuid %L', new.uuid);
    end if;

    return new;
end;
$function$
language plpgsql;


create trigger on_event_insert
    before insert
    on sourcing.eventstore
    for each row
        execute procedure sourcing.on_event();
