
from pathlib import Path
import pandas as pd

# Locate project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Dataset location
FILE_PATH = PROJECT_DIR / "data" / "source" / "telco_churn.csv"

# Check file existence
if not FILE_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {FILE_PATH}")

# Load dataset
df = pd.read_csv(FILE_PATH)

print("\n========== DATASET OVERVIEW ==========")

print("Total rows:", df.shape[0])
print("Total columns:", df.shape[1])

print("\n========== COLUMN NAMES ==========")
print(df.columns.tolist())

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

print("\n========== DUPLICATE CUSTOMER IDs ==========")
print(df["customerID"].duplicated().sum())

print("\n========== CHURN DISTRIBUTION ==========")
print(df["Churn"].value_counts(dropna=False))

print("\n========== NUMERICAL SUMMARY ==========")
print(df.describe())

print("\n========== TOTAL CHARGES CHECK ==========")
print("Blank TotalCharges:",
      df["TotalCharges"].astype(str).str.strip().eq("").sum())

print("\n========== SAMPLE RECORDS ==========")
print(df.head())

print("\nProfiling completed successfully!")


print("\n========== BLANK TOTAL CHARGES RECORDS ==========")

blank_mask = (
    df["TotalCharges"]
    .astype(str)
    .str.strip()
    .eq("")
)

blank_records = df.loc[
    blank_mask,
    ["customerID", "tenure", "MonthlyCharges", "TotalCharges", "Churn"]
]

print(blank_records.to_string(index=False))

print("\nNumber of blank records:", len(blank_records))

print("\nTenure of blank records:")
print(blank_records["tenure"].value_counts())

