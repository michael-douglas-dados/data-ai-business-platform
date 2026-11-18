select
    c.id as customer_id,
    c.segment,
    count(o.id) as frequency,
    coalesce(sum(o.amount_cents), 0) as monetary_cents,
    max(o.day) as last_purchase
from {{ source('raw', 'customers') }} c
left join {{ source('raw', 'orders') }} o on c.id = o.customer_id
    and o.day <= cast('2026-11-17' as date)
group by c.id, c.segment
