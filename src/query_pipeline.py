import sys

# Allow imports from the src directory
sys.path.insert(
    0,
    "src"
)

from query_processing import normalize_query
from intent_entity import analyze_query


def process_user_query(query):
    """
    Complete Module 2 -> Module 3 pipeline.

    Flow:

        Original Query
              ↓
        Module 2
              ↓
        Normalized Query
              ↓
        Module 3
              ↓
        Intent + Entities
    """

    # ------------------------------------------
    # MODULE 2: QUERY PROCESSING
    # ------------------------------------------

    module2_result = normalize_query(query)

    normalized_query = module2_result[
        "normalized_text"
    ]

    # ------------------------------------------
    # MODULE 3: INTENT & ENTITY DETECTION
    # ------------------------------------------

    module3_result = analyze_query(
        normalized_query
    )

    # ------------------------------------------
    # COMBINED RESULT
    # ------------------------------------------

    return {
        "original_query": query,
        "normalized_query": normalized_query,
        "intent": module3_result["intent"],
        "states": module3_result["states"],
        "districts": module3_result["districts"]
    }


def main():

    print(
        "=========================================="
    )
    print(
        " INGRES Module 2 → Module 3 Pipeline"
    )
    print(
        "=========================================="
    )

    query = input(
        "\nEnter your query: "
    )

    result = process_user_query(
        query
    )

    print(
        "\n------------------------------------------"
    )

    print("\nOriginal Query:")
    print(
        result["original_query"]
    )

    print("\nNormalized Query:")
    print(
        result["normalized_query"]
    )

    print("\nDetected Intent:")
    print(
        result["intent"]
    )

    print("\nDetected Entities:")

    print("States:")
    print(
        result["states"]
    )

    print("Districts:")
    print(
        result["districts"]
    )

    print(
        "\n------------------------------------------"
    )

    print(
        "Module 2 → Module 3 Pipeline Successful!"
    )


if __name__ == "__main__":
    main()