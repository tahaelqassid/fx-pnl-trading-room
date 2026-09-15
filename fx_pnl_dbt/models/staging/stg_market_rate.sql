select
    currency_pair,
    rate_date,
    closing_rate,
    source as rate_source
from {{ source('raw', 'market_rate') }}