CREATE TABLE book (
    id                    SERIAL PRIMARY KEY,
    name                  VARCHAR(50) NOT NULL,
    trader_id             VARCHAR(50) NOT NULL,
    accounting_currency   VARCHAR(3)  NOT NULL DEFAULT 'MAD',
    default_method        VARCHAR(4)  NOT NULL CHECK (default_method IN ('FIFO','WAC')),
    UNIQUE (name),
    stop_loss_threshold_mad NUMERIC(18,2) NOT NULL DEFAULT 50000
    );

CREATE TABLE trade (
    id             BIGSERIAL PRIMARY KEY,
    book_id        INTEGER NOT NULL REFERENCES book(id),
    currency_pair  VARCHAR(7) NOT NULL,
    direction      VARCHAR(4) NOT NULL CHECK (direction IN ('BUY','SELL')),
    nominal        NUMERIC(18,2) NOT NULL CHECK (nominal > 0),
    rate           NUMERIC(18,6) NOT NULL CHECK (rate > 0),
    trade_ts       TIMESTAMP NOT NULL,
    confidence     VARCHAR(10) NOT NULL DEFAULT 'confirmed'
                   CHECK (confidence IN ('manual','confirmed','simulated')),
    source_ref     VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE market_rate (
    currency_pair  VARCHAR(7) NOT NULL,
    rate_date      DATE NOT NULL,
    closing_rate   NUMERIC(18,6) NOT NULL CHECK (closing_rate > 0),
    source         VARCHAR(50) NOT NULL,
    PRIMARY KEY (currency_pair, rate_date)
);


CREATE TABLE daily_pnl (
    book_id         INTEGER NOT NULL REFERENCES book(id),
    pnl_date        DATE NOT NULL,
    realized_mad    NUMERIC(18,2) NOT NULL,
    unrealized_mad  NUMERIC(18,2) NOT NULL,
    total_mad       NUMERIC(18,2) NOT NULL,
    method_used     VARCHAR(4) NOT NULL CHECK (method_used IN ('FIFO','WAC')),
    PRIMARY KEY (book_id, pnl_date),
    CHECK (total_mad = realized_mad + unrealized_mad)
);


