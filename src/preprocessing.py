import os
import re
import pandas as pd


# ---------------------------------------------------------
# 1. Resolve project paths
# ---------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "INGRES_Step1_Cleaned_Dataset.csv")


# ---------------------------------------------------------
# 2. Load the cleaned dataset
# ---------------------------------------------------------

def load_cleaned_data():
    """Loads the cleaned groundwater dataset."""

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            f"Cleaned dataset not found at: {CSV_PATH}. "
            "Run datacleaning.py first."
        )

    df = pd.read_csv(CSV_PATH)

    print(f"Loaded {len(df)} records from cleaned dataset.")

    return df


# ---------------------------------------------------------
# 3. Basic text preprocessing
# ---------------------------------------------------------

def clean_text(text):
    """
    Performs basic text cleaning.

    Used mainly for text fields such as groundwater
    quality parameters.
    """

    if pd.isna(text):
        return ""

    text = str(text)

    # Convert to lowercase
    text = text.lower()

    # Remove unwanted characters
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ---------------------------------------------------------
# 4. Prepare text columns
# ---------------------------------------------------------

def preprocess_text_columns(df):
    """
    Cleans the text-based columns used by the retrieval
    and RAG components.
    """

    text_columns = [
        "STATE",
        "DISTRICT",
        "ASSESSMENT_UNIT",
        "Major_Quality_Parameters",
        "Other_Quality_Parameters",
        "Extraction_Category"
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].apply(clean_text)

    return df


# ---------------------------------------------------------
# 5. Create searchable text
# ---------------------------------------------------------

def create_search_text(row):
    """
    Combines important groundwater information into one
    searchable text representation.
    """

    parts = [
        f"state {row.get('STATE', '')}",
        f"district {row.get('DISTRICT', '')}",
        f"assessment unit {row.get('ASSESSMENT_UNIT', '')}",
        f"groundwater status {row.get('Extraction_Category', '')}",
        f"major quality parameters {row.get('Major_Quality_Parameters', '')}",
        f"other quality parameters {row.get('Other_Quality_Parameters', '')}"
    ]

    return " ".join(parts)


# ---------------------------------------------------------
# 6. Prepare complete dataset for retrieval
# ---------------------------------------------------------

def prepare_dataset():
    """
    Loads and preprocesses the cleaned groundwater dataset.
    """

    df = load_cleaned_data()

    # Clean text fields
    df = preprocess_text_columns(df)

    # Create a combined searchable text field
    df["search_text"] = df.apply(create_search_text, axis=1)

    return df


# ---------------------------------------------------------
# 7. Test the preprocessing module
# ---------------------------------------------------------

if __name__ == "__main__":

    print("----- INGRES Preprocessing -----")

    df = prepare_dataset()

    print("\nDataset shape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nSample searchable text:")

    if len(df) > 0:
        print(df["search_text"].iloc[0])
