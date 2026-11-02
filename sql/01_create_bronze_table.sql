CREATE TABLE IF NOT EXISTS bronze.customer_churn_raw (

    raw_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    customer_id TEXT,
    gender TEXT,
    senior_citizen TEXT,
    partner TEXT,
    dependents TEXT,
    tenure TEXT,
    phone_service TEXT,
    multiple_lines TEXT,
    internet_service TEXT,
    online_security TEXT,
    online_backup TEXT,
    device_protection TEXT,
    tech_support TEXT,
    streaming_tv TEXT,
    streaming_movies TEXT,
    contract TEXT,
    paperless_billing TEXT,
    payment_method TEXT,
    monthly_charges TEXT,
    total_charges TEXT,
    churn TEXT,

    batch_id UUID NOT NULL,
    source_file TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP

);