import os
import sqlite3
import pandas as pd


# --------------------------------------------------
# PATHS
# --------------------------------------------------

SCRIPT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BASE_DIR = os.path.dirname(
    SCRIPT_DIR
)

DB_PATH = os.path.join(
    BASE_DIR,
    "data",
    "ingres_groundwater.db"
)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database not found at: {DB_PATH}"
        )

    return sqlite3.connect(DB_PATH)


# --------------------------------------------------
# GET GROUNDWATER STATUS
# --------------------------------------------------

def get_groundwater_status(
    state=None,
    district=None
):

    query = """
        SELECT
            STATE,
            DISTRICT,
            ASSESSMENT_UNIT,
            Stage_of_Ground_Water_Extraction_pct,
            Extraction_Category
        FROM groundwater_reports
        WHERE 1 = 1
    """

    params = []

    # State filter
    if state:

        query += """
            AND LOWER(STATE) = LOWER(?)
        """

        params.append(state)

    # District filter
    if district:

        query += """
            AND LOWER(DISTRICT) = LOWER(?)
        """

        params.append(district)

    query += """
        ORDER BY STATE, DISTRICT
    """

    conn = get_connection()

    try:

        result = pd.read_sql_query(
            query,
            conn,
            params=params
        )

    finally:

        conn.close()

    return result


# --------------------------------------------------
# GET GROUNDWATER EXTRACTION
# --------------------------------------------------

def get_groundwater_extraction(
    state=None,
    district=None
):

    query = """
        SELECT
            STATE,
            DISTRICT,
            Stage_of_Ground_Water_Extraction_pct,
            Extraction_Category
        FROM groundwater_reports
        WHERE 1 = 1
    """

    params = []

    # State filter
    if state:

        query += """
            AND LOWER(STATE) = LOWER(?)
        """

        params.append(state)

    # District filter
    if district:

        query += """
            AND LOWER(DISTRICT) = LOWER(?)
        """

        params.append(district)

    query += """
        ORDER BY STATE, DISTRICT
    """

    conn = get_connection()

    try:

        result = pd.read_sql_query(
            query,
            conn,
            params=params
        )

    finally:

        conn.close()

    return result


# --------------------------------------------------
# TEST
# --------------------------------------------------

def main():

    print(
        "----- INGRES Module 4: Database Query -----"
    )

    print("\nTesting Jaisalmer, Rajasthan...")

    result = get_groundwater_status(
        state="Rajasthan",
        district="Jaisalmer"
    )

    print("\nDatabase Result:")

    print(result)

    print(
        "\n----- Database Query Successful -----"
    )


if __name__ == "__main__":
    main()