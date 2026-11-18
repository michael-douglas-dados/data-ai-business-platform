select source.total as source_total, mart.total as mart_total
from (
    select coalesce(sum(amount_cents), 0) as total
    from {{ source('raw', 'orders') }}
    where day <= cast('2026-11-17' as date)
) source
cross join (
    select coalesce(sum(revenue_cents), 0) as total
    from {{ ref('monthly_revenue') }}
) mart
where source.total <> mart.total
