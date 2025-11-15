CREATE TABLE IF NOT EXISTS processed_logs (
    ip String,
    url String,
    status UInt16,
    ts DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY ts;
