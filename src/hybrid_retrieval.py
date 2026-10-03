import sys

sys.path.insert(0, "src")

from database_query import (
    get_groundwater_status,
    get_groundwater_extraction
)

from ranking_filtering import (
    rank_by_extraction,
    get_top_n
)

from vector_rag import query_vector_store


# --------------------------------------------------
# MODULE 9: HYBRID RETRIEVAL
# --------------------------------------------------

def detect_requested_fields(query):
    """
    Detects which groundwater attributes are requested
    by the user.
    """

    query_lower = query.lower()

    fields = []

    # Groundwater extraction
    if (
        "extract" in query_lower
        or "exploitation" in query_lower
        or "stage" in query_lower
    ):
        fields.append("extraction")

    # Rainfall
    if (
        "rainfall" in query_lower
        or "rainfal" in query_lower
    ):
        fields.append("rainfall")

    # Groundwater recharge
    if (
        "recharge" in query_lower
        or "recharg" in query_lower
    ):
        fields.append("recharge")

    # Groundwater quality
    if (
        "quality" in query_lower
        or "qualiti" in query_lower
    ):
        fields.append("quality")

    # Status
    if "status" in query_lower:
        fields.append("status")

    return fields


# --------------------------------------------------
# STRUCTURED RETRIEVAL
# --------------------------------------------------

def structured_retrieval(
    intent,
    query,
    state=None,
    district=None,
    top_k=5
):
    """
    Retrieves exact structured groundwater data
    from SQLite.
    """

    requested_fields = detect_requested_fields(
        query
    )

    # If no specific field was detected,
    # use extraction as default.
    if not requested_fields:

        requested_fields = [
            "extraction"
        ]

    # ----------------------------------------------
    # BASE DATABASE QUERY
    # ----------------------------------------------

    if intent == "GROUNDWATER_STATUS":

        result = get_groundwater_status(
            state=state,
            district=district
        )

    else:

        result = get_groundwater_extraction(
            state=state,
            district=district
        )

    if result is None or result.empty:

        return result

    # ----------------------------------------------
    # ADDITIONAL DATA FROM DATABASE
    # ----------------------------------------------

    # The extraction query already contains:
    # STATE
    # DISTRICT
    # Stage_of_Ground_Water_Extraction_pct
    # Extraction_Category

    # For rainfall/recharge we need the complete
    # dataset directly from SQLite.

    if (
        "rainfall" in requested_fields
        or "recharge" in requested_fields
        or "quality" in requested_fields
    ):

        import sqlite3
        import os
        import pandas as pd

        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        db_path = os.path.join(
            base_dir,
            "data",
            "ingres_groundwater.db"
        )

        conn = sqlite3.connect(
            db_path
        )

        query_sql = """
            SELECT *
            FROM groundwater_reports
            WHERE 1 = 1
        """

        params = []

        if state:

            query_sql += """
                AND LOWER(STATE) = LOWER(?)
            """

            params.append(state)

        if district:

            query_sql += """
                AND LOWER(DISTRICT) = LOWER(?)
            """

            params.append(district)

        query_sql += """
            ORDER BY STATE, DISTRICT
        """

        result = pd.read_sql_query(
            query_sql,
            conn,
            params=params
        )

        conn.close()

    # ----------------------------------------------
    # RANKING
    # ----------------------------------------------

    if "extraction" in requested_fields:

        result = rank_by_extraction(
            result,
            ascending=False
        )

    elif "rainfall" in requested_fields:

        if "Rainfall_mm" in result.columns:

            result = result.sort_values(
                by="Rainfall_mm",
                ascending=False
            )

    elif "recharge" in requested_fields:

        if (
            "Annual_Ground_Water_Recharge_ham"
            in result.columns
        ):

            result = result.sort_values(
                by="Annual_Ground_Water_Recharge_ham",
                ascending=False
            )

    # ----------------------------------------------
    # TOP N
    # ----------------------------------------------

    return result.head(
        top_k
    ).copy()


# --------------------------------------------------
# SEMANTIC RETRIEVAL
# --------------------------------------------------

def semantic_retrieval(
    query,
    top_k=5
):
    """
    Retrieves semantically similar groundwater
    records from Chroma.
    """

    return query_vector_store(
        query,
        top_k=top_k
    )


# --------------------------------------------------
# HYBRID RETRIEVAL
# --------------------------------------------------

def hybrid_retrieve(
    query,
    intent,
    state=None,
    district=None,
    top_k=5
):
    """
    Combines structured SQL retrieval with
    semantic vector retrieval.
    """

    structured_results = structured_retrieval(
        intent=intent,
        query=query,
        state=state,
        district=district,
        top_k=top_k
    )

    semantic_results = semantic_retrieval(
        query,
        top_k=top_k
    )

    return {
        "structured_results": structured_results,
        "semantic_results": semantic_results
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

def main():

    print("==============================================")
    print(" INGRES MODULE 9: HYBRID RETRIEVAL")
    print("==============================================")

    query = input(
        "\nEnter a groundwater query: "
    )

    result = hybrid_retrieve(
        query=query,
        intent="GROUNDWATER_EXTRACTION",
        state=None,
        district=None,
        top_k=5
    )

    # ----------------------------------------------
    # STRUCTURED RESULTS
    # ----------------------------------------------

    print("\n==============================================")
    print("TOP STRUCTURED RESULTS")
    print("==============================================")

    structured = result[
        "structured_results"
    ]

    if (
        structured is not None
        and not structured.empty
    ):

        display_columns = [
            "STATE",
            "DISTRICT"
        ]

        if (
            "Stage_of_Ground_Water_Extraction_pct"
            in structured.columns
        ):

            display_columns.append(
                "Stage_of_Ground_Water_Extraction_pct"
            )

        if (
            "Extraction_Category"
            in structured.columns
        ):

            display_columns.append(
                "Extraction_Category"
            )

        if "Rainfall_mm" in structured.columns:

            display_columns.append(
                "Rainfall_mm"
            )

        if (
            "Annual_Ground_Water_Recharge_ham"
            in structured.columns
        ):

            display_columns.append(
                "Annual_Ground_Water_Recharge_ham"
            )

        print(
            structured[
                display_columns
            ].to_string(index=False)
        )

    else:

        print(
            "No structured results found."
        )

    # ----------------------------------------------
    # SEMANTIC RESULTS
    # ----------------------------------------------

    print("\n==============================================")
    print("SEMANTIC VECTOR RESULTS")
    print("==============================================")

    semantic = result[
        "semantic_results"
    ]

    for i, doc in enumerate(
        semantic,
        1
    ):

        print(
            f"\n--- Semantic Result {i} ---"
        )

        print(
            doc.page_content
        )

    print("\n==============================================")
    print("Hybrid Retrieval Test Complete!")
    print("==============================================")


if __name__ == "__main__":

    main()