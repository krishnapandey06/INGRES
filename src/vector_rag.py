import os
import shutil
import pandas as pd

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

SCRIPT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BASE_DIR = os.path.dirname(SCRIPT_DIR)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

CSV_PATH = os.path.join(
    DATA_DIR,
    "INGRES_Step1_Cleaned_Dataset.csv"
)

CHROMA_DB_DIR = os.path.join(
    DATA_DIR,
    "chroma_db"
)

COLLECTION_NAME = "ingres_groundwater"


# --------------------------------------------------
# EMBEDDING MODEL
# --------------------------------------------------

EMBEDDING_MODEL = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# --------------------------------------------------
# BUILD VECTOR STORE
# --------------------------------------------------

def build_vector_store():

    print(
        f"Loading cleaned dataset from {CSV_PATH}..."
    )

    if not os.path.exists(CSV_PATH):

        raise FileNotFoundError(
            f"Missing source file: {CSV_PATH}"
        )

    # ----------------------------------------------
    # REMOVE OLD VECTOR DATABASE
    # ----------------------------------------------

    if os.path.exists(CHROMA_DB_DIR):

        print(
            "\nRemoving existing Chroma database..."
        )

        shutil.rmtree(
            CHROMA_DB_DIR
        )

    # ----------------------------------------------
    # LOAD DATASET
    # ----------------------------------------------

    df = pd.read_csv(
        CSV_PATH
    )

    documents = []
    document_ids = []

    # ----------------------------------------------
    # CREATE DOCUMENTS
    # ----------------------------------------------

    for idx, row in df.iterrows():

        text_profile = (
            f"State: {row['STATE']}\n"
            f"District: {row['DISTRICT']}\n"
            f"Assessment Unit: "
            f"{row['ASSESSMENT_UNIT']}\n"
            f"Groundwater Status: "
            f"{row['Extraction_Category']} "
            f"(Stage of Extraction: "
            f"{row['Stage_of_Ground_Water_Extraction_pct']}%)\n"
            f"Annual Recharge: "
            f"{row['Annual_Ground_Water_Recharge_ham']} ham\n"
            f"Total Extraction: "
            f"{row['Total_Ground_Water_Extraction_ham']} ham "
            f"(Irrigation: "
            f"{row['Extraction_Irrigation_ham']} ham, "
            f"Domestic: "
            f"{row['Extraction_Domestic_ham']} ham, "
            f"Industrial: "
            f"{row['Extraction_Industrial_ham']} ham)\n"
            f"Major Quality Parameters: "
            f"{row['Major_Quality_Parameters']}\n"
            f"Other Quality Parameters: "
            f"{row['Other_Quality_Parameters']}\n"
            f"Rainfall: "
            f"{row['Rainfall_mm']} mm"
        )

        metadata = {
            "state": str(
                row["STATE"]
            ).lower(),

            "district": str(
                row["DISTRICT"]
            ).lower(),

            "category": str(
                row["Extraction_Category"]
            ),

            "stage_pct": float(
                row[
                    "Stage_of_Ground_Water_Extraction_pct"
                ]
            ),

            "row_id": int(idx)
        }

        document = Document(
            page_content=text_profile,
            metadata=metadata
        )

        documents.append(
            document
        )

        # Unique ID for every dataset row
        document_ids.append(
            f"groundwater_{idx}"
        )

    print(
        f"Created {len(documents)} "
        f"document profiles."
    )

    # ----------------------------------------------
    # CREATE VECTOR STORE
    # ----------------------------------------------

    print(
        "Generating embeddings..."
    )

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=EMBEDDING_MODEL,
        ids=document_ids,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DB_DIR
    )

    print(
        "\nVector Database successfully "
        f"created at: {CHROMA_DB_DIR}"
    )

    print(
        f"Collection: {COLLECTION_NAME}"
    )

    return vector_store


# --------------------------------------------------
# QUERY VECTOR STORE
# --------------------------------------------------

def query_vector_store(
    query_text: str,
    top_k: int = 3
):

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DB_DIR,
        embedding_function=EMBEDDING_MODEL
    )

    results = vector_store.similarity_search(
        query_text,
        k=top_k
    )

    return results


# --------------------------------------------------
# MAIN TEST
# --------------------------------------------------

if __name__ == "__main__":

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    # Build vector store
    build_vector_store()

    # ----------------------------------------------
    # SEMANTIC SEARCH TESTS
    # ----------------------------------------------

    test_queries = [
        "districts with very high groundwater extraction",
        "districts receiving very high rainfall",
        "districts with groundwater quality problems"
    ]

    for query in test_queries:

        print("\n==============================================")
        print("Semantic Search Query:")
        print(query)
        print("==============================================")

        results = query_vector_store(
            query,
            top_k=5
        )

        for i, doc in enumerate(results, 1):

            print(
                f"\n--- Result {i} ---"
            )

            print(
                doc.page_content
            )