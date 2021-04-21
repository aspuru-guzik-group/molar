-- create a human readable id for the synthesis
create or replace function public.create_synthesis_hid (new record)
returns record as $new$
declare
    hid character varying(16) := '';
    owner_lab_id uuid;
    rec record;
begin
    if (select exists(select synthesis_machine_id 
                        from public.synthesis_machine as sm 
                       where sm.synthesis_machine_id = (select new.data->>'synthesis_machine_id')::uuid
        )) then

        -- lab owning the machine
        owner_lab_id = (select lab.lab_id from public.lab as lab 
                          join public.synthesis_machine as sm using(lab_id)
                         where sm.synthesis_machine_id = (select new.data->>'synthesis_machine_id')::uuid);

        hid = format('%s_%s_%s',
            (select lab.short_name from public.lab where lab_id = owner_lab_id),
            (select to_char(new.timestamp, 'YYYY-MM-DD')),
            (select  count(*)
               from public.synthesis as syn
    left outer join public.synthesis_machine as sm using(synthesis_machine_id)
               join public.lab as lab using(lab_id)
              where lab.lab_id = owner_lab_id
                and syn.created_on > date_trunc('day', new.timestamp) - interval '1 day'));
        
        new.data = jsonb_insert(new.data, '{hid}', quote_ident((hid::text))::jsonb);
        return new;
    else
        raise using message = format('could not find machine with the provided id %s', synth_machine_id);
    end if;
end;
$new$
language plpgsql;

create or replace function public.add_synthesis_hid( )
return trigger as $function$
begin
  if new.type = 'synthesis' and not new.data ? 'hid' then
    new = (select public.create_synthesis_hid(new));
  end if;
  return new;
end;
$function$
language plpgsql


create trigger add_synthesis_hid
  before insert
  on sourcing.eventstore
  for each row
    execute procedure public.add_synthesis_hid();
