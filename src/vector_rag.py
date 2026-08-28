import os
import pandas as pd
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Resolve paths safely
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.getcwd()

BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "INGRES_Step1_Cleaned_Dataset.csv")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")

# Singleton embedding configuration (saves memory)
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def build_vector_store():
    """Converts CSV rows into rich textual documents and indexes them into ChromaDB."""
    print(f"Loading cleaned dataset from {CSV_PATH}...")
    
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Missing source file: {CSV_PATH}")
        
    df = pd.read_csv(CSV_PATH)
    documents = []
    
    for idx, row in df.iterrows():
        text_profile = (
            f"State: {row['STATE']}\n"
            f"District: {row['DISTRICT']}\n"
            f"Assessment Unit: {row['ASSESSMENT_UNIT']}\n"
            f"Groundwater Status: {row['Extraction_Category']} (Stage of Extraction: {row['Stage_of_Ground_Water_Extraction_pct']}%)\n"
            f"Annual Recharge: {row['Annual_Ground_Water_Recharge_ham']} ham\n"
            f"Total Extraction: {row['Total_Ground_Water_Extraction_ham']} ham "
            f"(Irrigation: {row['Extraction_Irrigation_ham']} ham, Domestic: {row['Extraction_Domestic_ham']} ham, Industrial: {row['Extraction_Industrial_ham']} ham)\n"
            f"Major Quality Parameters: {row['Major_Quality_Parameters']}\n"
            f"Other Quality Parameters: {row['Other_Quality_Parameters']}\n"
            f"Rainfall: {row['Rainfall_mm']} mm"
        )
        
        metadata = {
            "state": str(row['STATE']).lower(),
            "district": str(row['DISTRICT']).lower(),
            "category": str(row['Extraction_Category']),
            "stage_pct": float(row['Stage_of_Ground_Water_Extraction_pct'])
        }
        
        documents.append(Document(page_content=text_profile, metadata=metadata))
        
    print(f"Created {len(documents)} document profiles. Generating embeddings...")
    
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=EMBEDDING_MODEL,
        persist_directory=CHROMA_DB_DIR
    )
    print(f"Vector Database successfully created at: {CHROMA_DB_DIR}")
    return vector_store

def query_vector_store(query_text: str, top_k: int = 3):
    """Executes similarity search on the indexed vector store."""
    vector_store = Chroma(
        persist_directory=CHROMA_DB_DIR, 
        embedding_function=EMBEDDING_MODEL
    )
    results = vector_store.similarity_search(query_text, k=top_k)
    return results

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    build_vector_store()
    
    print("\n--- Testing Vector Search ---")
    test_hits = query_vector_store("districts with quality issues or high extraction")
    
    for i, doc in enumerate(test_hits, 1):
        print(f"\n[Result {i}]:\n{doc.page_content}")
