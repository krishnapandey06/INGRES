import pandas as pd


# --------------------------------------------------
# BASIC STATISTICS
# --------------------------------------------------

def calculate_statistics(result):
    """
    Calculate basic groundwater extraction
    statistics from retrieved records.
    """

    if result is None or result.empty:
        return {}

    extraction = result[
        "Stage_of_Ground_Water_Extraction_pct"
    ]

    return {
        "total_records": len(result),
        "average_extraction": extraction.mean(),
        "maximum_extraction": extraction.max(),
        "minimum_extraction": extraction.min()
    }


# --------------------------------------------------
# HIGHEST EXTRACTION DISTRICT
# --------------------------------------------------

def get_highest_extraction(result):
    """
    Find the district with the highest
    groundwater extraction.
    """

    if result is None or result.empty:
        return None

    row = result.loc[
        result[
            "Stage_of_Ground_Water_Extraction_pct"
        ].idxmax()
    ]

    return {
        "state": row["STATE"],
        "district": row["DISTRICT"],
        "extraction": row[
            "Stage_of_Ground_Water_Extraction_pct"
        ],
        "category": row["Extraction_Category"]
    }


# --------------------------------------------------
# LOWEST EXTRACTION DISTRICT
# --------------------------------------------------

def get_lowest_extraction(result):
    """
    Find the district with the lowest
    groundwater extraction.
    """

    if result is None or result.empty:
        return None

    row = result.loc[
        result[
            "Stage_of_Ground_Water_Extraction_pct"
        ].idxmin()
    ]

    return {
        "state": row["STATE"],
        "district": row["DISTRICT"],
        "extraction": row[
            "Stage_of_Ground_Water_Extraction_pct"
        ],
        "category": row["Extraction_Category"]
    }


# --------------------------------------------------
# CATEGORY DISTRIBUTION
# --------------------------------------------------

def get_category_distribution(result):
    """
    Count districts belonging to each
    groundwater extraction category.
    """

    if result is None or result.empty:
        return {}

    distribution = (
        result["Extraction_Category"]
        .value_counts()
        .to_dict()
    )

    return distribution


# --------------------------------------------------
# COMPLETE ANALYSIS
# --------------------------------------------------

def analyze_groundwater(result):
    """
    Perform complete groundwater analysis.
    """

    if result is None or result.empty:
        return {}

    statistics = calculate_statistics(
        result
    )

    highest = get_highest_extraction(
        result
    )

    lowest = get_lowest_extraction(
        result
    )

    distribution = get_category_distribution(
        result
    )

    return {
        "statistics": statistics,
        "highest_extraction": highest,
        "lowest_extraction": lowest,
        "category_distribution": distribution
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

def main():

    print(
        "----- INGRES Module 6: Data Analysis -----"
    )

    import sys

    sys.path.insert(0, "src")

    from database_query import (
        get_groundwater_extraction
    )

    # Get Tamilnadu data
    result = get_groundwater_extraction(
        state="Tamilnadu"
    )

    # Analyze data
    analysis = analyze_groundwater(
        result
    )

    print("\nBasic Statistics:")

    print(
        analysis["statistics"]
    )

    print("\nHighest Extraction:")

    print(
        analysis["highest_extraction"]
    )

    print("\nLowest Extraction:")

    print(
        analysis["lowest_extraction"]
    )

    print("\nCategory Distribution:")

    print(
        analysis["category_distribution"]
    )

    print(
        "\n----- Data Analysis Successful -----"
    )


if __name__ == "__main__":
    main()