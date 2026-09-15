select
    id as trade_id,
    book_id,
    currency_pair,
    direction,
    nominal,
    rate,
    trade_ts,
    confidence
from {{ source('raw', 'trade') }}