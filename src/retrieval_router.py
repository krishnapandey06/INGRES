import sys

sys.path.insert(0, "src")

from query_pipeline import process_user_query
from hybrid_retrieval import hybrid_retrieve


# --------------------------------------------------
# MODULE 9: RETRIEVAL ROUTER
# --------------------------------------------------

def determine_retrieval_mode(
    original_query,
    normalized_query,
    intent
):
    """
    Determines whether the query requires
    structured, semantic, or hybrid retrieval.
    """

    original_lower = original_query.lower()
    normalized_lower = normalized_query.lower()

    # Combine original and normalized query so that
    # useful words removed during preprocessing are
    # still available for retrieval routing.
    combined_query = (
        original_lower + " " + normalized_lower
    )

    # ----------------------------------------------
    # STRUCTURED KEYWORDS
    # ----------------------------------------------

    structured_keywords = [
        "extract",
        "extraction",
        "recharg",
        "recharge",
        "rainfal",
        "rainfall",
        "status",
        "percent",
        "percentage",
        "highest",
        "lowest",
        "maximum",
        "minimum",
        "averag",
        "average",
        "top",
        "bottom",
        "how much"
    ]

    # ----------------------------------------------
    # SEMANTIC KEYWORDS
    # ----------------------------------------------

    semantic_keywords = [
        "information",
        "inform",
        "explain",
        "describe",
        "related",
        "about",
        "issues",
        "issue",
        "problems",
        "problem",
        "quality",
        "qualiti",
        "concerns",
        "concern"
    ]

    has_structured_keyword = any(
        keyword in combined_query
        for keyword in structured_keywords
    )

    has_semantic_keyword = any(
        keyword in combined_query
        for keyword in semantic_keywords
    )

    # ----------------------------------------------
    # HYBRID
    # ----------------------------------------------

    if (
        has_structured_keyword
        and has_semantic_keyword
    ):
        return "HYBRID"

    # ----------------------------------------------
    # STRUCTURED
    # ----------------------------------------------

    if has_structured_keyword:
        return "STRUCTURED"

    # ----------------------------------------------
    # SEMANTIC
    # ----------------------------------------------

    if has_semantic_keyword:
        return "SEMANTIC"

    # ----------------------------------------------
    # DEFAULT BASED ON INTENT
    # ----------------------------------------------

    if intent in [
        "GROUNDWATER_STATUS",
        "GROUNDWATER_EXTRACTION",
        "GROUNDWATER_RECHARGE",
        "RAINFALL",
        "EXTRACTION_STATUS"
    ]:
        return "STRUCTURED"

    return "SEMANTIC"


# --------------------------------------------------
# ROUTE QUERY
# --------------------------------------------------

def route_query(query):

    # ----------------------------------------------
    # MODULE 2 + MODULE 3
    # ----------------------------------------------

    analysis = process_user_query(
        query
    )

    normalized_query = analysis[
        "normalized_query"
    ]

    intent = analysis[
        "intent"
    ]

    states = analysis[
        "states"
    ]

    districts = analysis[
        "districts"
    ]

    state = (
        states[0]
        if states
        else None
    )

    district = (
        districts[0]
        if districts
        else None
    )

    # ----------------------------------------------
    # DETERMINE RETRIEVAL MODE
    # ----------------------------------------------

    mode = determine_retrieval_mode(
        original_query=query,
        normalized_query=normalized_query,
        intent=intent
    )

    # ----------------------------------------------
    # STRUCTURED RETRIEVAL
    # ----------------------------------------------

    if mode == "STRUCTURED":

        result = hybrid_retrieve(
            query=normalized_query,
            intent=intent,
            state=state,
            district=district,
            top_k=5
        )

        result["semantic_results"] = []

    # ----------------------------------------------
    # SEMANTIC RETRIEVAL
    # ----------------------------------------------

    elif mode == "SEMANTIC":

        result = hybrid_retrieve(
            query=normalized_query,
            intent="UNKNOWN",
            state=None,
            district=None,
            top_k=5
        )

        result["structured_results"] = None

    # ----------------------------------------------
    # HYBRID RETRIEVAL
    # ----------------------------------------------

    elif mode == "HYBRID":

        result = hybrid_retrieve(
            query=normalized_query,
            intent=intent,
            state=state,
            district=district,
            top_k=5
        )

    # ----------------------------------------------
    # SAFETY FALLBACK
    # ----------------------------------------------

    else:

        result = {
            "structured_results": None,
            "semantic_results": []
        }

    return {
        "query": query,
        "normalized_query": normalized_query,
        "intent": intent,
        "states": states,
        "districts": districts,
        "retrieval_mode": mode,
        "structured_results": result[
            "structured_results"
        ],
        "semantic_results": result[
            "semantic_results"
        ]
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

def main():

    print(
        "=============================================="
    )

    print(
        " INGRES RETRIEVAL ROUTER"
    )

    print(
        "=============================================="
    )

    while True:

        query = input(
            "\nEnter query (or 'exit'): "
        ).strip()

        if query.lower() == "exit":

            print(
                "\nRouter test finished."
            )

            break

        if not query:

            continue

        result = route_query(
            query
        )

        print(
            "\n----------------------------------------------"
        )

        print(
            "\nOriginal Query:"
        )

        print(
            result["query"]
        )

        print(
            "\nNormalized Query:"
        )

        print(
            result["normalized_query"]
        )

        print(
            "\nDetected Intent:"
        )

        print(
            result["intent"]
        )

        print(
            "\nRetrieval Mode:"
        )

        print(
            result["retrieval_mode"]
        )

        print(
            "\nDetected States:"
        )

        print(
            result["states"]
        )

        print(
            "\nDetected Districts:"
        )

        print(
            result["districts"]
        )

        # ------------------------------------------
        # STRUCTURED RESULTS
        # ------------------------------------------

        structured = result[
            "structured_results"
        ]

        if (
            structured is not None
            and not structured.empty
        ):

            print(
                "\nTOP STRUCTURED RESULTS:"
            )

            print(
                structured.to_string(
                    index=False
                )
            )

        # ------------------------------------------
        # SEMANTIC RESULTS
        # ------------------------------------------

        semantic = result[
            "semantic_results"
        ]

        if semantic:

            print(
                "\nSEMANTIC RESULTS:"
            )

            for i, doc in enumerate(
                semantic,
                1
            ):

                print(
                    f"\n--- Result {i} ---"
                )

                print(
                    doc.page_content
                )

        print(
            "\n----------------------------------------------"
        )


# --------------------------------------------------
# PROGRAM START
# --------------------------------------------------

if __name__ == "__main__":

    main()