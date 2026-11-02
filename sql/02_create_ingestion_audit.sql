CREATE TABLE IF NOT EXISTS bronze.ingestion_audit (

    batch_id UUID PRIMARY KEY,

    source_file TEXT NOT NULL,

    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMPTZ,

    input_records INTEGER NOT NULL DEFAULT 0,

    loaded_records INTEGER NOT NULL DEFAULT 0,

    invalid_records INTEGER NOT NULL DEFAULT 0,

    status TEXT NOT NULL,

    error_message TEXT

);