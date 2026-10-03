import os
import pandas as pd


# ---------------------------------------------------------
# INGRES - Module 1
# Data Preprocessing & Validation
# ---------------------------------------------------------

# Resolve project paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_CSV_PATH = os.path.join(
    DATA_DIR,
    "INGRES_Step1_Cleaned_Dataset.csv"
)


def load_cleaned_dataset():
    """Load the cleaned groundwater dataset."""

    if not os.path.exists(INPUT_CSV_PATH):
        raise FileNotFoundError(
            f"Cleaned dataset not found at:\n{INPUT_CSV_PATH}\n"
            "Run datacleaning.py first."
        )

    df = pd.read_csv(INPUT_CSV_PATH)

    return df


def validate_dataset(df):
    """Validate the cleaned dataset for Module 1 requirements."""

    print("\n----- INGRES Module 1: Data Validation -----")

    # -----------------------------------------------------
    # Basic information
    # -----------------------------------------------------

    print(f"Total records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    # -----------------------------------------------------
    # Required hierarchy columns
    # -----------------------------------------------------

    hierarchy_columns = [
        "STATE",
        "DISTRICT",
        "ASSESSMENT_UNIT"
    ]

    missing_columns = [
        column
        for column in hierarchy_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing hierarchy columns: {missing_columns}"
        )

    print("\nHierarchy columns:")
    print("STATE → DISTRICT → ASSESSMENT_UNIT")

    # -----------------------------------------------------
    # Check missing hierarchy values
    # -----------------------------------------------------

    print("\nMissing hierarchy values:")

    missing_values = df[hierarchy_columns].isna().sum()

    print(missing_values)

    if missing_values.sum() == 0:
        print("✓ No missing hierarchy values")
    else:
        print("⚠ Missing hierarchy values detected")

    # -----------------------------------------------------
    # Check duplicate complete records
    # -----------------------------------------------------

    duplicate_rows = df.duplicated().sum()

    print(f"\nDuplicate complete records: {duplicate_rows}")

    if duplicate_rows == 0:
        print("✓ No duplicate records")
    else:
        print("⚠ Duplicate records detected")

    # -----------------------------------------------------
    # Check STATE + DISTRICT uniqueness
    # -----------------------------------------------------

    duplicate_hierarchy = df.duplicated(
        subset=["STATE", "DISTRICT"]
    ).sum()

    print(
        f"Duplicate STATE + DISTRICT combinations: "
        f"{duplicate_hierarchy}"
    )

    if duplicate_hierarchy == 0:
        print("✓ STATE + DISTRICT combinations are unique")
    else:
        print("⚠ Duplicate STATE + DISTRICT combinations detected")

    # -----------------------------------------------------
    # Unique hierarchy information
    # -----------------------------------------------------

    print("\nHierarchy statistics:")
    print(f"Unique states: {df['STATE'].nunique()}")
    print(f"Unique districts: {df['DISTRICT'].nunique()}")
    print(
        f"Unique assessment units: "
        f"{df['ASSESSMENT_UNIT'].nunique()}"
    )

    # -----------------------------------------------------
    # Check assessment unit
    # -----------------------------------------------------

    print("\nAssessment units:")
    print(df["ASSESSMENT_UNIT"].value_counts())

    # -----------------------------------------------------
    # Dataset validation summary
    # -----------------------------------------------------

    print("\n----- Validation Summary -----")

    checks = {
        "Records present": len(df) > 0,
        "Required hierarchy columns present": not missing_columns,
        "No missing hierarchy values":
            missing_values.sum() == 0,
        "No duplicate complete records":
            duplicate_rows == 0,
        "Unique STATE + DISTRICT":
            duplicate_hierarchy == 0
    }

    for check, result in checks.items():
        status = "PASS" if result else "FAIL"
        print(f"{status}: {check}")

    if all(checks.values()):
        print("\n✓ Module 1 dataset validation successful!")
    else:
        print("\n⚠ Module 1 validation requires attention.")

    return df


def main():
    print("----- INGRES Preprocessing -----")
    print(f"Loading dataset from:\n{INPUT_CSV_PATH}")

    df = load_cleaned_dataset()

    print("\nDataset loaded successfully.")

    validate_dataset(df)


if __name__ == "__main__":
    main()