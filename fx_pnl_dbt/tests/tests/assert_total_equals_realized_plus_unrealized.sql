select *
from {{ source('raw', 'daily_pnl') }}
where round(total_mad, 2) != round(realized_mad + unrealized_mad, 2)