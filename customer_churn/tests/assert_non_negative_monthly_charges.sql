SELECT *
FROM {{ ref('stg_customer_churn') }}
WHERE monthly_charges < 0