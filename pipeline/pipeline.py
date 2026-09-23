import os
import sqlite3
import logging
from datetime import datetime
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_FILE = os.path.join(BASE_DIR, "data", "raw", "Bookings.csv")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
PROCESSED_FILE = os.path.join(PROCESSED_DIR, "clean_bookings.csv")
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_FILE = os.path.join(DATABASE_DIR, "rideflow.db")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "pipeline.log")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_raw_data():
    logging.info("Starting data ingestion...")

    if not os.path.exists(RAW_FILE):
        raise FileNotFoundError(
            f"Bookings.csv not found at: {RAW_FILE}"
        )

    df = pd.read_csv(RAW_FILE)

    logging.info(f"Raw records loaded: {len(df)}")

    return df


def clean_data(df):
    logging.info("Starting data cleaning...")

    df = df.dropna(axis=1, how="all")

    unwanted_columns = [
        "Vehicle Images",
        "Unnamed: 20"
    ]

    df = df.drop(
        columns=[
            col for col in unwanted_columns
            if col in df.columns
        ],
        errors="ignore"
    )

    df.columns = [
        col.strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
        for col in df.columns
    ]

    if "booking_id" in df.columns:
        df = df.drop_duplicates(
            subset=["booking_id"]
        )

    text_columns = df.select_dtypes(
        include=["object"]
    ).columns

    for col in text_columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )

    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    numeric_columns = [
        "v_tat",
        "c_tat",
        "canceled_rides_by_customer",
        "canceled_rides_by_driver",
        "incomplete_rides",
        "booking_value",
        "ride_distance",
        "driver_ratings",
        "customer_rating"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    logging.info(
        f"Cleaning completed: {len(df)} records"
    )

    return df


def validate_data(df):
    logging.info("Starting data validation...")

    required_columns = [
        "booking_id",
        "booking_status",
        "date",
        "vehicle_type",
        "pickup_location",
        "drop_location"
    ]

    existing_required = [
        col for col in required_columns
        if col in df.columns
    ]

    df["is_valid"] = (
        df[existing_required]
        .notna()
        .all(axis=1)
    )

    if "booking_value" in df.columns:
        df.loc[
            df["booking_value"] < 0,
            "is_valid"
        ] = False

    if "ride_distance" in df.columns:
        df.loc[
            df["ride_distance"] < 0,
            "is_valid"
        ] = False

    valid = int(df["is_valid"].sum())
    invalid = int((~df["is_valid"]).sum())

    logging.info(
        f"Validation completed: "
        f"Valid={valid}, Invalid={invalid}"
    )

    return df


def transform_data(df):
    logging.info("Starting transformation...")

    if "date" in df.columns:
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["day"] = df["date"].dt.day
        df["month_name"] = df["date"].dt.month_name()

    if "booking_status" in df.columns:
        df["is_successful"] = (
            df["booking_status"]
            .astype(str)
            .str.lower()
            .eq("success")
        )

    if "ride_distance" in df.columns:
        df["distance_category"] = pd.cut(
            df["ride_distance"],
            bins=[
                -float("inf"),
                5,
                15,
                30,
                float("inf")
            ],
            labels=[
                "Short",
                "Medium",
                "Long",
                "Very Long"
            ]
        )

    logging.info("Transformation completed.")

    return df


def save_processed_data(df):
    df.to_csv(
        PROCESSED_FILE,
        index=False
    )

    logging.info(
        f"Processed data saved: {PROCESSED_FILE}"
    )


def load_to_database(df):
    logging.info("Loading data into SQLite...")

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    valid_df = df[
        df["is_valid"] == True
    ].copy()

    valid_df.to_sql(
        "bookings",
        connection,
        if_exists="replace",
        index=False
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_time TEXT,
            total_records INTEGER,
            valid_records INTEGER,
            invalid_records INTEGER,
            status TEXT
        )
    """)

    total = len(df)
    valid = len(valid_df)
    invalid = total - valid

    cursor.execute("""
        INSERT INTO pipeline_runs
        (
            run_time,
            total_records,
            valid_records,
            invalid_records,
            status
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        total,
        valid,
        invalid,
        "SUCCESS"
    ))

    connection.commit()
    connection.close()

    logging.info(
        "SQLite loading completed."
    )


def run_pipeline():

    print()
    print("=" * 65)
    print("       RIDEFLOW DATA ENGINEERING PIPELINE")
    print("=" * 65)

    print("\n[1/5] DATA INGESTION")

    df = load_raw_data()

    print(f"Raw Records: {len(df):,}")

    print("\n[2/5] DATA CLEANING")

    df = clean_data(df)

    print(f"After Cleaning: {len(df):,}")

    print("\n[3/5] DATA VALIDATION")

    df = validate_data(df)

    valid = int(df["is_valid"].sum())
    invalid = int((~df["is_valid"]).sum())

    print(f"Valid Records: {valid:,}")
    print(f"Invalid Records: {invalid:,}")

    print("\n[4/5] DATA TRANSFORMATION")

    df = transform_data(df)

    print("Transformation completed.")

    print("\n[5/5] DATA STORAGE")

    save_processed_data(df)
    load_to_database(df)

    print("\nProcessed CSV:")
    print(PROCESSED_FILE)

    print("\nSQLite Database:")
    print(DATABASE_FILE)

    print()
    print("=" * 65)
    print("       PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 65)

    return df
