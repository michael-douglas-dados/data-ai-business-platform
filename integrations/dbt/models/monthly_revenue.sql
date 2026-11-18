select
    date_trunc('month', day)::date as month,
    count(*) as orders,
    sum(amount_cents) as revenue_cents
from {{ source('raw', 'orders') }}
where day <= cast('2026-11-17' as date)
group by 1
