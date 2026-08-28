import os
import sqlite3
import pandas as pd

# 1. Resolve Paths Dynamically
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "INGRES_Step1_Cleaned_Dataset.csv")
DB_PATH = os.path.join(DATA_DIR, "ingres_groundwater.db")

def init_sqlite_db():
    """Reads the cleaned CSV and converts it into a SQLite database table."""
    print(f"Loading data from: {CSV_PATH}")
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Cleaned CSV not found at {CSV_PATH}. Run datacleaning.py first.")
    
    df = pd.read_csv(CSV_PATH)
    
    # Establish SQLite Connection
    conn = sqlite3.connect(DB_PATH)
    
    # Export DataFrame to SQLite Table 'groundwater_reports'
    df.to_sql('groundwater_reports', conn, if_exists='replace', index=False)
    
    print(f"Database successfully created at: {DB_PATH}")
    conn.close()

def execute_sql_query(query: str):
    """Utility function to execute a SQL query and return results as a Pandas DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    try:
        result_df = pd.read_sql_query(query, conn)
        conn.close()
        return result_df
    except Exception as e:
        conn.close()
        return f"SQL Execution Error: {e}"

if __name__ == "__main__":
    # Initialize the Database
    init_sqlite_db()
    
    # Test Query 1: Count Total Districts
    test_1 = execute_sql_query("SELECT COUNT(*) AS Total_Districts FROM groundwater_reports;")
    print("\n[Test Query 1] Total Districts in DB:")
    print(test_1)
    
    # Test Query 2: Find Top 5 Over-Exploited Districts
    test_2 = execute_sql_query("""
        SELECT STATE, DISTRICT, Stage_of_Ground_Water_Extraction_pct, Extraction_Category 
        FROM groundwater_reports 
        WHERE Extraction_Category = 'Over-Exploited' 
        ORDER BY Stage_of_Ground_Water_Extraction_pct DESC 
        LIMIT 5;
    """)
    print("\n[Test Query 2] Top 5 Most Over-Exploited Districts:")
    print(test_2)
