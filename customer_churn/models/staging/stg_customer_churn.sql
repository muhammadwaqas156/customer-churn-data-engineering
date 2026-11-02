WITH source_data AS (

    SELECT *
    FROM {{ source('bronze', 'customer_churn_raw') }}

),

cleaned_data AS (

    SELECT
        raw_id,
        TRIM(customer_id) AS customer_id,
        TRIM(gender) AS gender,

        NULLIF(TRIM(senior_citizen), '')::INTEGER AS senior_citizen,

        TRIM(partner) AS partner,
        TRIM(dependents) AS dependents,

        NULLIF(TRIM(tenure), '')::INTEGER AS tenure,

        TRIM(phone_service) AS phone_service,
        TRIM(multiple_lines) AS multiple_lines,
        TRIM(internet_service) AS internet_service,
        TRIM(online_security) AS online_security,
        TRIM(online_backup) AS online_backup,
        TRIM(device_protection) AS device_protection,
        TRIM(tech_support) AS tech_support,
        TRIM(streaming_tv) AS streaming_tv,
        TRIM(streaming_movies) AS streaming_movies,
        TRIM(contract) AS contract,
        TRIM(paperless_billing) AS paperless_billing,
        TRIM(payment_method) AS payment_method,

        NULLIF(TRIM(monthly_charges), '')::NUMERIC(10,2)
            AS monthly_charges,

        NULLIF(TRIM(total_charges), '')::NUMERIC(10,2)
            AS total_charges,

        TRIM(churn) AS churn,

        batch_id,
        source_file,
        ingested_at

    FROM source_data

)

SELECT *
FROM cleaned_data