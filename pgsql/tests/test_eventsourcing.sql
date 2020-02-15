begin;

-- test fixture
create table public.test (
    "created_on" timestamp without time zone,
    "updated_on" timestamp without time zone,
    "id" uuid primary key not null,
    "test" text,
    "test_arr" float8[],
    "test_json" jsonb,
    "test_varchar" character varying (3),
    "test_int" integer
);


select plan(6);


-- testing on_create_query
insert into sourcing.eventstore 
       (event,     type,   data)
values ('create', 'test', '{"test": "asdfasdf", "test_arr": [0, 1, 2], "test_json": {"test": "test"}, "test_varchar": "asd", "test_int": 0}'::jsonb);

select results_eq(
    'select test, 
            test_arr, 
            test_json, 
            test_varchar,
            test_int from public.test',
    $$
        VALUES ('asdfasdf', 
                '{0, 1, 2}'::float8[], 
                '{"test": "test"}'::jsonb, 
                'asd'::character varying(3),
                0::integer)
    $$,
    'create event failed!'
);


-- testing on_update_query
insert into sourcing.eventstore 
       (event,     type,   data, uuid)
values ('update', 'test', 
        '{"test": "asdf", "test_arr": [1, 0, 2], "test_json": {"test": "asdf"}, "test_varchar": "fds", "test_int": 1}'::jsonb,
        (select id from test)
);


select results_eq(
    'select test, test_arr, test_json, test_varchar, test_int from public.test',
    $$
        values ('asdf', 
                '{1, 0, 2}'::float8[],
                '{"test": "asdf"}'::jsonb,
                'fds'::character varying(3),
                1::integer)
    $$,
    'create event failed!'
);

-- testing on_update_query without uuid
prepare "update_statement" AS insert into sourcing.eventstore 
       (event,     type,   data)
values ('update', 'test', 
        '{"test": "asdf", "test_arr": [1, 0, 2], "test_json": {"test": "asdf"}}'::jsonb)    
;

select throws_ok('"update_statement"', 22004, 'No uuid has been provided'); 


-- testing on_update_query with a uuid that does not exists
prepare "update_statement2" AS insert into sourcing.eventstore 
       (event,     type,   data, uuid)
values ('update', 'test', 
        '{"test": "asdf", "test_arr": [1, 0, 2], "test_json": {"test": "asdf"}}'::jsonb,
        uuid_generate_v4())    
;

select throws_ok('"update_statement2"', 'P0002'); 


-- testing on_delete_query
prepare "delete_statement" as insert into sourcing.eventstore
        (event,     type, uuid, timestamp)
values ('delete', 'test', (select id from public.test), now() + interval '1 second');


select performs_ok('"delete_statement"', 100);

-- testing on_rollback_query
insert into sourcing.eventstore
       (event, timestamp,     data)
values ('rollback', 
        now() + interval '1 second',
        format('{"before": "%s"}',
               (select timestamp 
                  from sourcing.eventstore
                 where event = 'delete'))::jsonb);

select results_eq(
    'select count(*)::int from test',
    $$ values (1::int) $$,
    'test rollback');



-- removing test fixture
drop table if exists public.test;

commit;
