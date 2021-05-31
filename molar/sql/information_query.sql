select 
  cols.table_name,
  cols.column_name,
  data_type,
  udt_name,
  is_nullable,
  tc.constraint_name,
  tc.constraint_type,
  ccu.table_name || '.' || ccu.column_name as references
from 
  information_schema.columns as cols
left join
  information_schema.key_column_usage as kcu
  on
    kcu.table_name = cols.table_name
  and
    kcu.column_name = cols.column_name
left join
  information_schema.table_constraints as tc
  on
    tc.table_name = cols.table_name
  and
    tc.constraint_name = kcu.constraint_name
left join
  information_schema.constraint_column_usage as ccu
  on
    ccu.constraint_name = tc.constraint_name
where 
  cols.table_schema = 'public' 
and 
  cols.table_name != 'alembic_version'
order by
  cols.table_name, cols.column_name;
