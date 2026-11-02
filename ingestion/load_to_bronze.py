import pandas as pd
import psycopg2
import uuid
import logging
from psycopg2.extras import execute_values
from pathlib import Path
from datetime import datetime, timezone
from getpass import getpass
import hashlib


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_FILE = BASE_DIR / "data" / "source" / "telco_churn.csv"


# Database configuration
DB_NAME = "customer_churn_db"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"


# Generate a unique batch ID for this ingestion run
BATCH_ID = str(uuid.uuid4())

# Source filename
SOURCE_FILE = CSV_FILE.name



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Expected source columns
EXPECTED_COLUMNS = [
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn"
]


def read_source_data():

    logging.info("Starting source data validation.")

    # Check whether the CSV file exists
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"Source CSV file not found: {CSV_FILE}"
        )

    # Read all source columns as text.
    # Keep blank strings rather than converting them to NaN.
    df = pd.read_csv(
        CSV_FILE,
        dtype=str,
        keep_default_na=False
    )

    logging.info("Source CSV loaded successfully.")

    # Check expected columns
    missing_columns = set(EXPECTED_COLUMNS) - set(df.columns)
    unexpected_columns = set(df.columns) - set(EXPECTED_COLUMNS)

    if missing_columns:
        raise ValueError(
            f"Missing expected columns: {missing_columns}"
        )

    if unexpected_columns:
        logging.warning(
            f"Unexpected columns found: {unexpected_columns}"
        )

    # Check source row count
    logging.info(f"Input records: {len(df)}")
    logging.info(f"Input columns: {len(df.columns)}")

    # Count blank TotalCharges values
    blank_total_charges = (
        df["TotalCharges"].str.strip().eq("").sum()
    )

    logging.info(
        f"Blank TotalCharges records: {blank_total_charges}"
    )

    return df




def connect_to_database():

    logging.info("Connecting to PostgreSQL.")

    password = getpass("Enter PostgreSQL password: ")

    connection = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=password,
        host=DB_HOST,
        port=DB_PORT
    )

    logging.info("PostgreSQL connection successful.")

    return connection

def insert_into_bronze(df, connection):

    logging.info("Preparing records for Bronze ingestion.")

    # Map CSV column names to PostgreSQL column names
    column_mapping = {
        "customerID": "customer_id",
        "gender": "gender",
        "SeniorCitizen": "senior_citizen",
        "Partner": "partner",
        "Dependents": "dependents",
        "tenure": "tenure",
        "PhoneService": "phone_service",
        "MultipleLines": "multiple_lines",
        "InternetService": "internet_service",
        "OnlineSecurity": "online_security",
        "OnlineBackup": "online_backup",
        "DeviceProtection": "device_protection",
        "TechSupport": "tech_support",
        "StreamingTV": "streaming_tv",
        "StreamingMovies": "streaming_movies",
        "Contract": "contract",
        "PaperlessBilling": "paperless_billing",
        "PaymentMethod": "payment_method",
        "MonthlyCharges": "monthly_charges",
        "TotalCharges": "total_charges",
        "Churn": "churn"
    }

    df = df.rename(columns=column_mapping)

    # Add ingestion metadata
    df["batch_id"] = BATCH_ID
    df["source_file"] = SOURCE_FILE
    df["ingested_at"] = datetime.now(timezone.utc)

    columns = list(df.columns)

    records = list(
        df.itertuples(index=False, name=None)
    )

    query = f"""
        INSERT INTO bronze.customer_churn_raw
        ({", ".join(columns)})
        VALUES %s
    """

    try:
        with connection.cursor() as cursor:

            execute_values(
                cursor,
                query,
                records,
                page_size=1000
            )

        

        logging.info(
            f"Successfully inserted {len(records)} records."
        )

        return len(records)

    except Exception:

        connection.rollback()

        logging.exception(
            "Bronze ingestion failed. Transaction rolled back."
        )

        raise
    
    
def start_audit(connection, input_records, source_hash):

    query = """
        INSERT INTO bronze.ingestion_audit (
            batch_id,
            source_file,
            source_hash,
            input_records,
            status
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                BATCH_ID,
                SOURCE_FILE,
                source_hash,
                input_records,
                "RUNNING"
            )
        )

    connection.commit()

    logging.info("Ingestion audit started.")


def complete_audit(connection, loaded_records):

    query = """
        UPDATE bronze.ingestion_audit
        SET
            completed_at = CURRENT_TIMESTAMP,
            loaded_records = %s,
            status = 'SUCCESS'
        WHERE batch_id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (loaded_records, BATCH_ID))

    connection.commit()

    logging.info("Ingestion audit completed successfully.")
    
    
def fail_audit(connection, error_message):

    query = """
        UPDATE bronze.ingestion_audit
        SET
            completed_at = CURRENT_TIMESTAMP,
            status = 'FAILED',
            error_message = %s
        WHERE batch_id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (str(error_message)[:2000], BATCH_ID)
        )

    connection.commit()

    logging.error("Ingestion failure recorded in audit table.")    
    
def check_batch_exists(connection, source_hash):

    query = """
        SELECT batch_id
        FROM bronze.ingestion_audit
        WHERE source_hash = %s
        AND status = 'SUCCESS'
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (source_hash,))
        result = cursor.fetchone()

    if result:
        raise ValueError(
            "This source file has already been loaded successfully. "
            f"Previous batch ID: {result[0]}"
        )

    return False   
 
 
def calculate_file_hash():

    sha256 = hashlib.sha256()

    with open(CSV_FILE, "rb") as file:

        for chunk in iter(
            lambda: file.read(4096),
            b""
        ):
            sha256.update(chunk)

    return sha256.hexdigest()



    test_batch_id = str(uuid.uuid4())

    try:
        # 1. Create a RUNNING audit record
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO bronze.ingestion_audit (
                    batch_id,
                    source_file,
                    source_hash,
                    input_records,
                    status
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                test_batch_id,
                "failure_test.csv",
                "controlled_failure_test",
                1,
                "RUNNING"
            ))

        connection.commit()

        # 2. Start the Bronze transaction
        try:
            with connection.cursor() as cursor:

                cursor.execute("""
                    INSERT INTO bronze.customer_churn_raw (
                        customer_id,
                        batch_id,
                        source_file
                    )
                    VALUES (%s, %s, %s)
                """, (
                    "TEST_CUSTOMER",
                    test_batch_id,
                    "failure_test.csv"
                ))

                # Deliberately trigger a database error
                cursor.execute("""
                    INSERT INTO bronze.non_existing_test_table
                    (test_value)
                    VALUES ('trigger failure')
                """)

            connection.commit()

        except Exception as error:

            connection.rollback()

            # 3. Record the failure separately
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE bronze.ingestion_audit
                    SET
                        completed_at = CURRENT_TIMESTAMP,
                        status = 'FAILED',
                        error_message = %s
                    WHERE batch_id = %s
                """, (str(error)[:2000], test_batch_id))

            connection.commit()

            logging.exception("Controlled test failure recorded.")

    except Exception:
        connection.rollback()
        raise

    return test_batch_id     

if __name__ == "__main__":

    connection = None
    audit_started = False

    try:
        # 1. Read source data
        df = read_source_data()

        # 2. Calculate source fingerprint
        source_hash = calculate_file_hash()

        logging.info(f"Source SHA-256: {source_hash}")

        # 3. Connect to PostgreSQL
        connection = connect_to_database()

        # 4. Prevent duplicate source ingestion
        check_batch_exists(connection, source_hash)

        # 5. Register ingestion attempt
        start_audit(
            connection,
            len(df),
            source_hash
        )

        audit_started = True

        # 6. Load records into Bronze
        loaded_records = insert_into_bronze(
            df,
            connection
        )

        # 7. Mark batch successful
        complete_audit(
            connection,
            loaded_records
        )

        print("\n========== INGESTION SUMMARY ==========")
        print(f"Batch ID: {BATCH_ID}")
        print(f"Source file: {SOURCE_FILE}")
        print(f"Source records: {len(df)}")
        print(f"Loaded records: {loaded_records}")
        print("Status: SUCCESS")
        print("=======================================")

    except Exception as error:

        logging.exception("Ingestion pipeline failed.")

        if connection is not None and audit_started:
            try:
                connection.rollback()

                fail_audit(connection, error)

            except Exception:
                logging.exception("Could not update ingestion audit.")

        raise

    finally:

        if connection is not None:
            connection.close()
            logging.info("Database connection closed.") 