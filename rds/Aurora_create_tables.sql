CREATE TABLE trades (
    trade_id BIGINT PRIMARY KEY,
    xid VARCHAR(50),
    price NUMERIC,
    quantity INT,
    timestamp_eastern TIMESTAMP,
    order_value NUMERIC
);

CREATE TABLE etl_control (
    file_name TEXT PRIMARY KEY,
    load_time TIMESTAMP DEFAULT NOW()
);

CREATE TABLE staging_trades (
    trade_id BIGINT PRIMARY KEY,
    xid VARCHAR(50),
    price NUMERIC,
    quantity INT,
    timestamp_eastern TIMESTAMP,
    order_value NUMERIC
);
