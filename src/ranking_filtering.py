import pandas as pd


# --------------------------------------------------
# FILTER BY EXTRACTION CATEGORY
# --------------------------------------------------

def filter_by_category(
    result,
    category
):
    """
    Filter groundwater records by
    extraction category.
    """

    if result is None or result.empty:
        return result

    return result[
        result["Extraction_Category"]
        .str.lower()
        == category.lower()
    ].copy()


# --------------------------------------------------
# RANK BY EXTRACTION
# --------------------------------------------------

def rank_by_extraction(
    result,
    ascending=False
):
    """
    Rank groundwater records according to
    groundwater extraction percentage.
    """

    if result is None or result.empty:
        return result

    return result.sort_values(
        by="Stage_of_Ground_Water_Extraction_pct",
        ascending=ascending
    ).copy()


# --------------------------------------------------
# TOP N RESULTS
# --------------------------------------------------

def get_top_n(
    result,
    n=5
):
    """
    Return the top N records according to
    groundwater extraction percentage.
    """

    ranked = rank_by_extraction(
        result,
        ascending=False
    )

    if ranked is None:
        return ranked

    return ranked.head(n).copy()


# --------------------------------------------------
# BOTTOM N RESULTS
# --------------------------------------------------

def get_bottom_n(
    result,
    n=5
):
    """
    Return the bottom N records according to
    groundwater extraction percentage.
    """

    ranked = rank_by_extraction(
        result,
        ascending=True
    )

    if ranked is None:
        return ranked

    return ranked.head(n).copy()


# --------------------------------------------------
# TEST
# --------------------------------------------------

def main():

    print(
        "----- INGRES Module 5: Ranking & Filtering -----"
    )

    # Import database function
    import sys

    sys.path.insert(0, "src")

    from database_query import (
        get_groundwater_extraction
    )

    # Retrieve Tamilnadu records
    result = get_groundwater_extraction(
        state="Tamilnadu"
    )

    print("\nTop 5 districts by groundwater extraction:")

    top_results = get_top_n(
        result,
        n=5
    )

    print(
        top_results[
            [
                "STATE",
                "DISTRICT",
                "Stage_of_Ground_Water_Extraction_pct",
                "Extraction_Category"
            ]
        ].to_string(index=False)
    )

    print(
        "\n----- Ranking & Filtering Successful -----"
    )


if __name__ == "__main__":
    main()