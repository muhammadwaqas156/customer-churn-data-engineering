
# Customer Churn – Data Dictionary

| Column | Data Type | Description | Data Quality Rule |
|---|---|---|---|
| customerID | VARCHAR | Unique customer identifier | Required, unique |
| gender | VARCHAR | Customer gender | Female/Male |
| SeniorCitizen | INTEGER | Senior citizen indicator | 0 or 1 |
| Partner | VARCHAR | Has a partner | Yes/No |
| Dependents | VARCHAR | Has dependents | Yes/No |
| tenure | INTEGER | Months as a customer | >= 0 |
| PhoneService | VARCHAR | Has phone service | Yes/No |
| MultipleLines | VARCHAR | Multiple phone lines | Yes/No/No phone service |
| InternetService | VARCHAR | Internet service type | DSL/Fiber optic/No |
| OnlineSecurity | VARCHAR | Online security service | Yes/No/No internet service |
| OnlineBackup | VARCHAR | Online backup service | Yes/No/No internet service |
| DeviceProtection | VARCHAR | Device protection service | Yes/No/No internet service |
| TechSupport | VARCHAR | Technical support service | Yes/No/No internet service |
| StreamingTV | VARCHAR | Streaming TV service | Yes/No/No internet service |
| StreamingMovies | VARCHAR | Streaming movies service | Yes/No/No internet service |
| Contract | VARCHAR | Customer contract type | Month-to-month/One year/Two year |
| PaperlessBilling | VARCHAR | Paperless billing indicator | Yes/No |
| PaymentMethod | VARCHAR | Customer payment method | Valid source category |
| MonthlyCharges | NUMERIC | Monthly customer charges | >= 0 |
| TotalCharges | NUMERIC | Total customer charges | >= 0 or NULL |
| Churn | VARCHAR | Whether customer left | Yes/No |

## Source information

- Dataset: IBM Telco Customer Churn
- Total records: 7,043
- Total columns: 21
- Duplicate customer IDs: 0
- Blank TotalCharges: 11
- All 11 blank TotalCharges records have tenure = 0.

## Data quality decisions

- Preserve original source values in Bronze.
- Convert blank TotalCharges to NULL during transformation.
- Retain all 7,043 customers.
- Enforce unique customerID in the curated mart.
