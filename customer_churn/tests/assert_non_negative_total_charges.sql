SELECT *
FROM {{ ref('stg_customer_churn') }}
WHERE total_charges < 0