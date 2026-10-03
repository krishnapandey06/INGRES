import sys
import os
import sqlite3
import pandas as pd

sys.path.insert(0, "src")

from query_pipeline import process_user_query

from ranking_filtering import (
    rank_by_extraction
)

from data_analysis import (
    analyze_groundwater
)

from response_generator import (
    generate_response
)

from retrieval_router import (
    route_query
)


# --------------------------------------------------
# GET COMPLETE STRUCTURED DATA
# --------------------------------------------------

def get_complete_structured_data(
    state=None,
    district=None
):
    """
    Retrieves the complete structured dataset for
    the requested state/district.

    This is separate from Module 9 top-k retrieval.

    Module 9 may return only the top 5 records for
    ranking/display, but Module 6 needs all records
    for correct statistics.
    """

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

    if not os.path.exists(db_path):
        raise FileNotFoundError(
            f"Database not found at: {db_path}"
        )

    conn = sqlite3.connect(db_path)

    try:

        query = """
            SELECT *
            FROM groundwater_reports
            WHERE 1 = 1
        """

        params = []

        if state:

            query += """
                AND LOWER(STATE) = LOWER(?)
            """

            params.append(state)

        if district:

            query += """
                AND LOWER(DISTRICT) = LOWER(?)
            """

            params.append(district)

        query += """
            ORDER BY STATE, DISTRICT
        """

        result = pd.read_sql_query(
            query,
            conn,
            params=params
        )

    finally:

        conn.close()

    return result


# --------------------------------------------------
# FULL PIPELINE
# --------------------------------------------------

def run_full_pipeline(query):

    # --------------------------------------------------
    # MODULE 2 → MODULE 3
    # --------------------------------------------------

    analysis = process_user_query(query)

    intent = analysis["intent"]

    states = analysis["states"]

    districts = analysis["districts"]

    state = states[0] if states else None

    district = (
        districts[0]
        if districts
        else None
    )

    # --------------------------------------------------
    # MODULE 9: RETRIEVAL ROUTER
    # --------------------------------------------------

    retrieval_result = route_query(
        query
    )

    structured_result = retrieval_result[
        "structured_results"
    ]

    semantic_result = retrieval_result[
        "semantic_results"
    ]

    retrieval_mode = retrieval_result[
        "retrieval_mode"
    ]

    # --------------------------------------------------
    # COMPLETE STRUCTURED DATA
    # --------------------------------------------------
    #
    # Module 9 uses top-k retrieval for ranking.
    #
    # Module 6 needs ALL records for correct
    # state-level statistics.
    #
    # Example:
    # Tamil Nadu = 38 districts
    #
    # Module 9 → top 5
    # Module 6 → all 38
    #
    # --------------------------------------------------

    complete_structured_result = None

    if state or district:

        complete_structured_result = (
            get_complete_structured_data(
                state=state,
                district=district
            )
        )

    # --------------------------------------------------
    # RANKING FOR DISPLAY
    # --------------------------------------------------

    ranked_result = None

    if (
        complete_structured_result is not None
        and
        not complete_structured_result.empty
    ):

        if (
            "Stage_of_Ground_Water_Extraction_pct"
            in complete_structured_result.columns
        ):

            ranked_result = rank_by_extraction(
                complete_structured_result,
                ascending=False
            )

        else:

            ranked_result = (
                complete_structured_result
            )

    # --------------------------------------------------
    # MODULE 6: DATA ANALYSIS
    # --------------------------------------------------
    #
    # IMPORTANT:
    # Analyze the COMPLETE dataset, not top 5.
    #
    # --------------------------------------------------

    if (
        complete_structured_result is not None
        and
        not complete_structured_result.empty
        and
        "Stage_of_Ground_Water_Extraction_pct"
        in complete_structured_result.columns
    ):

        data_analysis = analyze_groundwater(
            complete_structured_result
        )

    else:

        data_analysis = {}

    # --------------------------------------------------
    # MODULE 7: RESPONSE GENERATION
    # --------------------------------------------------

    final_response = generate_response(
        intent=intent,
        analysis=data_analysis,
        state=state,
        district=district,
        structured_result=ranked_result,
        original_query=query
    )

    # --------------------------------------------------
    # RETURN COMPLETE PIPELINE RESULT
    # --------------------------------------------------

    return {

        "analysis": analysis,

        # Original Module 9 result
        "database_result": structured_result,

        # Complete state/district dataset
        "complete_structured_result":
            complete_structured_result,

        # Ranked complete dataset
        "ranked_result":
            ranked_result,

        # Module 6 analysis
        "data_analysis":
            data_analysis,

        # Final Module 7 response
        "response":
            final_response,

        # Module 9 mode
        "retrieval_mode":
            retrieval_mode,

        # Semantic results
        "semantic_results":
            semantic_result,

        # Complete retrieval result
        "retrieval_result":
            retrieval_result
    }


# --------------------------------------------------
# MAIN TEST
# --------------------------------------------------

def main():

    print(
        "================================================"
    )

    print(
        " INGRES COMPLETE PIPELINE"
    )

    print(
        " Module 2 → 3 → 9 → 5 → 6 → 7"
    )

    print(
        "================================================"
    )

    query = input(
        "\nEnter your query: "
    )

    result = run_full_pipeline(
        query
    )

    analysis = result[
        "analysis"
    ]

    data_analysis = result[
        "data_analysis"
    ]

    final_response = result[
        "response"
    ]

    retrieval_mode = result[
        "retrieval_mode"
    ]

    semantic_results = result[
        "semantic_results"
    ]

    # --------------------------------------------------
    # QUERY INFORMATION
    # --------------------------------------------------

    print(
        "\n------------------------------------------------"
    )

    print(
        "\nOriginal Query:"
    )

    print(
        analysis[
            "original_query"
        ]
    )

    print(
        "\nNormalized Query:"
    )

    print(
        analysis[
            "normalized_query"
        ]
    )

    print(
        "\nDetected Intent:"
    )

    print(
        analysis[
            "intent"
        ]
    )

    print(
        "\nDetected State:"
    )

    print(
        analysis[
            "states"
        ]
    )

    print(
        "\nDetected District:"
    )

    print(
        analysis[
            "districts"
        ]
    )

    # --------------------------------------------------
    # MODULE 9
    # --------------------------------------------------

    print(
        "\n------------------------------------------------"
    )

    print(
        "\nModule 9 Retrieval Mode:"
    )

    print(
        retrieval_mode
    )

    # --------------------------------------------------
    # TOP STRUCTURED RESULTS
    # --------------------------------------------------

    ranked_result = result[
        "ranked_result"
    ]

    if (
        ranked_result is not None
        and
        not ranked_result.empty
    ):

        print(
            "\nModule 9 / Ranked Structured Results:"
        )

        display_columns = [
            column
            for column in [
                "STATE",
                "DISTRICT",
                "Stage_of_Ground_Water_Extraction_pct",
                "Extraction_Category",
                "Rainfall_mm",
                "Annual_Ground_Water_Recharge_ham"
            ]
            if column in ranked_result.columns
        ]

        if display_columns:

            print(
                ranked_result[
                    display_columns
                ]
                .head(5)
                .to_string(index=False)
            )

        else:

            print(
                ranked_result
                .head(5)
                .to_string(index=False)
            )

    else:

        print(
            "\nNo structured results."
        )

    # --------------------------------------------------
    # SEMANTIC RESULTS
    # --------------------------------------------------

    if semantic_results:

        print(
            "\nModule 9 Semantic Results:"
        )

        for i, doc in enumerate(
            semantic_results,
            1
        ):

            print(
                f"\n--- Semantic Result {i} ---"
            )

            print(
                doc.page_content
            )

    # --------------------------------------------------
    # MODULE 6
    # --------------------------------------------------

    print(
        "\n------------------------------------------------"
    )

    print(
        "\nModule 6 Analysis:"
    )

    if data_analysis:

        print(
            "\nStatistics:"
        )

        print(
            data_analysis.get(
                "statistics",
                {}
            )
        )

        print(
            "\nHighest Extraction:"
        )

        print(
            data_analysis.get(
                "highest_extraction"
            )
        )

        print(
            "\nLowest Extraction:"
        )

        print(
            data_analysis.get(
                "lowest_extraction"
            )
        )

        print(
            "\nCategory Distribution:"
        )

        print(
            data_analysis.get(
                "category_distribution",
                {}
            )
        )

    else:

        print(
            "No analysis available."
        )

    # --------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------

    print(
        "\n------------------------------------------------"
    )

    print(
        "\nINGRES Response:\n"
    )

    print(
        final_response
    )

    print(
        "\n------------------------------------------------"
    )

    print(
        "INGRES Complete Pipeline Successful!"
    )


# --------------------------------------------------
# PROGRAM ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":

    main()