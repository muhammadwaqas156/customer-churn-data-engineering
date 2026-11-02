SELECT *
FROM {{ ref('stg_customer_churn') }}
WHERE tenure < 0