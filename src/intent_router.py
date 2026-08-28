import os
import re
from database_engine import execute_sql_query
from vector_rag import query_vector_store

def classify_intent(user_query: str) -> str:
    """Classifies user intent into SQL_METRIC, VECTOR_RAG, or GENERAL."""
    query_lower = user_query.lower()
    
    # SQL Keywords (Math, Aggregations, Rankings, Counts)
    sql_keywords = [
        "top", "highest", "lowest", "count", "average", "mean", "total", 
        "how many", "list all", "stage of extraction", "percentage", ">", "<", "="
    ]
    
    # Vector RAG Keywords (Quality parameters, safety descriptions, summaries)
    vector_keywords = [
        "quality", "fluoride", "arsenic", "salinity", "contaminant", 
        "tell me about", "summary", "overview", "report", "safe or not", "why"
    ]
    
    if any(k in query_lower for k in sql_keywords):
        return "SQL_METRIC"
    elif any(k in query_lower for k in vector_keywords):
        return "VECTOR_RAG"
    else:
        return "HYBRID"

def handle_user_query(user_query: str):
    """Main routing pipeline that directs prompt to SQLite or Vector Search."""
    intent = classify_intent(user_query)
    print(f"\n[Detected Intent]: {intent}")
    
    if intent == "SQL_METRIC":
        # Simple heuristic mapping or pass to LLM function caller
        if "over-exploited" in user_query.lower():
            sql = """
                SELECT STATE, DISTRICT, Stage_of_Ground_Water_Extraction_pct, Extraction_Category 
                FROM groundwater_reports 
                WHERE Extraction_Category = 'Over-Exploited' 
                ORDER BY Stage_of_Ground_Water_Extraction_pct DESC LIMIT 5;
            """
            return execute_sql_query(sql)
        else:
            # Fallback general query
            sql = f"SELECT STATE, DISTRICT, Stage_of_Ground_Water_Extraction_pct, Extraction_Category FROM groundwater_reports LIMIT 5;"
            return execute_sql_query(sql)
            
    elif intent == "VECTOR_RAG":
        docs = query_vector_store(user_query, top_k=3)
        return [d.page_content for d in docs]
        
    else:
        # Hybrid Approach: Returns both math stats and context
        sql_res = execute_sql_query("SELECT COUNT(*) AS Total FROM groundwater_reports;")
        rag_res = query_vector_store(user_query, top_k=2)
        return {
            "sql_summary": sql_res,
            "vector_context": [d.page_content for d in rag_res]
        }

if __name__ == "__main__":
    print("--- Test 1: Math / Metric Query ---")
    res1 = handle_user_query("Show me top over-exploited districts")
    print(res1)
    
    print("\n--- Test 2: Qualitative RAG Query ---")
    res2 = handle_user_query("Tell me about water quality parameters and contamination")
    print(res2)
