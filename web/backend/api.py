# --------------------------------------------------
# INGRES FASTAPI BACKEND
# --------------------------------------------------

import sys
import os
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# --------------------------------------------------
# PROJECT PATH
# --------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

SRC_PATH = os.path.join(
    PROJECT_ROOT,
    "src"
)

sys.path.append(SRC_PATH)


# --------------------------------------------------
# IMPORT INGRES PIPELINE
# --------------------------------------------------

from full_pipeline import run_full_pipeline


# --------------------------------------------------
# FASTAPI APP
# --------------------------------------------------

app = FastAPI(
    title="INGRES API"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# CHAT REQUEST
# --------------------------------------------------

class ChatRequest(BaseModel):

    query: str


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "INGRES API is running"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health")
def health():

    return {
        "success": True,
        "status": "healthy"
    }


# --------------------------------------------------
# DATASET ENDPOINT
# --------------------------------------------------

@app.get("/api/dataset")
def get_dataset():

    try:

        data_path = os.path.join(
            PROJECT_ROOT,
            "data",
            "INGRES_Step1_Cleaned_Dataset.csv"
        )

        df = pd.read_csv(
            data_path
        )

        df = df.where(
            pd.notnull(df),
            None
        )

        records = df.to_dict(
            orient="records"
        )

        return {
            "success": True,
            "count": len(records),
            "columns": list(df.columns),
            "data": records
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# --------------------------------------------------
# MAP DATA ENDPOINT
# --------------------------------------------------

@app.get("/api/map-data")
def get_map_data():

    try:

        data_path = os.path.join(
            PROJECT_ROOT,
            "data",
            "INGRES_Step1_Cleaned_Dataset.csv"
        )

        df = pd.read_csv(
            data_path
        )

        records = []

        for _, row in df.iterrows():

            records.append(
                {
                    "state": row.get(
                        "STATE",
                        None
                    ),

                    "district": row.get(
                        "DISTRICT",
                        None
                    ),

                    "category": row.get(
                        "Extraction_Category",
                        "Unknown"
                    ),

                    "extraction": row.get(
                        "Stage_of_Ground_Water_Extraction_pct",
                        None
                    )
                }
            )

        return {
            "success": True,
            "count": len(records),
            "data": records
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# --------------------------------------------------
# CHAT ENDPOINT
# --------------------------------------------------

@app.post("/api/chat")
def chat(request: ChatRequest):

    try:

        result = run_full_pipeline(
            request.query
        )

        # ------------------------------------------
        # Make sure frontend receives success=true
        # ------------------------------------------

        result["success"] = True

        # ------------------------------------------
        # Fix missing state in response text
        # ------------------------------------------

        if (
            result.get("district")
            and not result.get("state")
        ):

            database_result = result.get(
                "database_result",
                {}
            )

            if isinstance(
                database_result,
                dict
            ):

                state_values = database_result.get(
                    "STATE"
                )

                if isinstance(
                    state_values,
                    dict
                ) and state_values:

                    state = next(
                        iter(
                            state_values.values()
                        )
                    )

                    result["state"] = state

        return result

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# --------------------------------------------------
# RUN SERVER
# --------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )