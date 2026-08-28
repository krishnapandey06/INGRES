import os
import pandas as pd
import numpy as np

# 1. Dynamically locate the base folder (INGRES) and file paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))          # C:/Users/krishna/Desktop/INGRES/src
BASE_DIR = os.path.dirname(SCRIPT_DIR)                            # C:/Users/krishna/Desktop/INGRES

# Change 'data' below if your data folder has a different exact name (e.g., 'data' or 'Data')
INPUT_CSV_PATH = os.path.join(BASE_DIR, "data", "INGRES_Averaged_Groundwater_Dataset.csv")
OUTPUT_CSV_PATH = os.path.join(BASE_DIR, "data", "INGRES_Step1_Cleaned_Dataset.csv")

print(f"Reading dataset from: {INPUT_CSV_PATH}")

# 2. Load the dataset
try:
    df = pd.read_csv(INPUT_CSV_PATH)
except FileNotFoundError:
    # Fallback search if the data folder name varies
    print(f"File not found at {INPUT_CSV_PATH}. Checking base directory directly...")
    INPUT_CSV_PATH = os.path.join(BASE_DIR, "INGRES_Averaged_Groundwater_Dataset.csv")
    df = pd.read_csv(INPUT_CSV_PATH)

# 3. Clean Text / Quality Columns
df['Major_Quality_Parameters'] = df['Major_Quality_Parameters'].fillna('None Reported')
df['Other_Quality_Parameters'] = df['Other_Quality_Parameters'].fillna('None Reported')

# 4. Handle Invalid Zeros using State-Level Medians
invalid_zero_cols = ['Total_Geographical_Area_ha', 'Rainfall_mm', 'Recharge_Worthy_Area_Total_ha']
for col in invalid_zero_cols:
    if col in df.columns:
        df[col] = df[col].replace(0.0, np.nan)
        df[col] = df.groupby('STATE')[col].transform(lambda x: x.fillna(x.median()))
        df[col] = df[col].fillna(df[col].median()).round(2)

# 5. Categorize Groundwater Exploitation Stage
def categorize_stage(pct):
    if pd.isna(pct) or pct == 0:
        return 'Unknown'
    elif pct < 70:
        return 'Safe'
    elif 70 <= pct <= 90:
        return 'Semi-Critical'
    elif 90 < pct <= 100:
        return 'Critical'
    else:
        return 'Over-Exploited'

df['Extraction_Category'] = df['Stage_of_Ground_Water_Extraction_pct'].apply(categorize_stage)

# 6. Save Cleaned Dataset to Data Folder
df.to_csv(OUTPUT_CSV_PATH, index=False)

print("\nStep 1 Data Cleaning Successful!")
print(f"Cleaned output saved to: {OUTPUT_CSV_PATH}")
print(f"Total Rows Processed: {len(df)}")
