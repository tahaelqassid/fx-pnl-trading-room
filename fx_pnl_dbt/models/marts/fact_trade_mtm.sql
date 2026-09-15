with trades as (
    select
        trade_id,
        book_id,
        currency_pair,
        direction,
        nominal,
        rate,
        trade_ts,
        trade_ts::date as trade_date
    from {{ ref('stg_trade') }}
),

usd_mad as (
    select rate_date, closing_rate as usd_mad_rate
    from {{ ref('stg_market_rate') }}
    where currency_pair = 'USD/MAD'
),

direct_close as (
    select currency_pair, rate_date, closing_rate
    from {{ ref('stg_market_rate') }}
),

trade_with_rates as (
    select
        t.*,
        case
            when t.currency_pair = 'EUR/USD' then t.rate * u.usd_mad_rate
            else t.rate
        end as traded_rate_mad,
        case
            when t.currency_pair = 'EUR/USD' then
                (select closing_rate from direct_close
                 where currency_pair = 'EUR/MAD' and rate_date = t.trade_date)
            else
                (select closing_rate from direct_close
                 where currency_pair = t.currency_pair and rate_date = t.trade_date)
        end as closing_rate_mad
    from trades t
    left join usd_mad u on u.rate_date = t.trade_date
)

select
    trade_id,
    book_id,
    currency_pair,
    direction,
    nominal,
    trade_date,
    traded_rate_mad,
    closing_rate_mad,
    case
        when direction = 'BUY' then round((closing_rate_mad - traded_rate_mad) * nominal, 2)
        else round((traded_rate_mad - closing_rate_mad) * nominal, 2)
    end as mtm_pnl_mad
from trade_with_rates