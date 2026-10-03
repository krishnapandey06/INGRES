# --------------------------------------------------
# MODULE 7: RESPONSE GENERATION
# --------------------------------------------------


def format_number(value):
    return f"{float(value):.2f}"


def format_integer_number(value):
    return f"{float(value):,.2f}"


# --------------------------------------------------
# DISTRICT RESPONSE
# --------------------------------------------------

def generate_district_response(
    analysis,
    state=None,
    district=None
):
    if not analysis:
        return "No groundwater analysis is available."

    highest = analysis.get(
        "highest_extraction"
    )

    if not highest:
        return (
            "No groundwater data was found "
            "for this location."
        )

    extraction = highest["extraction"]
    category = highest["category"]

    return (
        f"Groundwater status for "
        f"{district}, {state}:\n\n"
        f"Groundwater extraction: "
        f"{format_number(extraction)}%\n"
        f"Status: {category}"
    )


# --------------------------------------------------
# DISTRICT FIELD RESPONSE
# --------------------------------------------------

def generate_district_field_response(
    result,
    state=None,
    district=None,
    original_query=None
):
    """
    Generates a response for a specific district
    based on the field requested by the user.
    """

    if result is None or result.empty:
        return (
            "No groundwater data was found "
            "for this location."
        )

    query = (
        original_query.lower()
        if original_query
        else ""
    )

    response = []

    # ----------------------------------------------
    # RAINFALL
    # ----------------------------------------------

    wants_rainfall = (
        "rainfall" in query
        or "rainfal" in query
    )

    if (
        wants_rainfall
        and "Rainfall_mm" in result.columns
    ):

        rainfall = result.iloc[0]["Rainfall_mm"]

        response.append(
            f"Rainfall information for "
            f"{district}, {state}:\n\n"
            f"Rainfall: "
            f"{format_number(rainfall)} mm"
        )

    # ----------------------------------------------
    # GROUNDWATER RECHARGE
    # ----------------------------------------------

    wants_recharge = (
        "recharge" in query
        or "recharg" in query
    )

    if (
        wants_recharge
        and
        "Annual_Ground_Water_Recharge_ham"
        in result.columns
    ):

        recharge = result.iloc[0][
            "Annual_Ground_Water_Recharge_ham"
        ]

        response.append(
            f"Groundwater recharge information "
            f"for {district}, {state}:\n\n"
            f"Annual groundwater recharge: "
            f"{format_integer_number(recharge)} ham"
        )

    # ----------------------------------------------
    # EXTRACTION
    # ----------------------------------------------

    wants_extraction = (
        "extract" in query
        or "extraction" in query
        or "exploitation" in query
    )

    if (
        wants_extraction
        and
        "Stage_of_Ground_Water_Extraction_pct"
        in result.columns
    ):

        extraction = result.iloc[0][
            "Stage_of_Ground_Water_Extraction_pct"
        ]

        category = result.iloc[0].get(
            "Extraction_Category",
            ""
        )

        response.append(
            f"Groundwater status for "
            f"{district}, {state}:\n\n"
            f"Groundwater extraction: "
            f"{format_number(extraction)}%\n"
            f"Status: {category}"
        )

    # ----------------------------------------------
    # FALLBACK
    # ----------------------------------------------

    if response:
        return "\n\n".join(response)

    return (
        "No specific groundwater field "
        "was identified in the query."
    )


# --------------------------------------------------
# STATE ANALYSIS RESPONSE
# --------------------------------------------------

def generate_state_analysis_response(
    analysis,
    state=None
):

    if not analysis:
        return (
            "No groundwater analysis is available."
        )

    statistics = analysis.get(
        "statistics",
        {}
    )

    highest = analysis.get(
        "highest_extraction"
    )

    lowest = analysis.get(
        "lowest_extraction"
    )

    distribution = analysis.get(
        "category_distribution",
        {}
    )

    response = []

    response.append(
        f"Groundwater extraction analysis "
        f"for {state}"
    )

    response.append(
        f"\nDistricts analyzed: "
        f"{statistics.get('total_records', 0)}"
    )

    response.append(
        "Average extraction: "
        f"{format_number(statistics.get('average_extraction', 0))}%"
    )

    if highest:

        response.append(
            "\nHighest extraction:"
        )

        response.append(
            f"• {highest['district']} — "
            f"{format_number(highest['extraction'])}% "
            f"({highest['category']})"
        )

    if lowest:

        response.append(
            "\nLowest extraction:"
        )

        response.append(
            f"• {lowest['district']} — "
            f"{format_number(lowest['extraction'])}% "
            f"({lowest['category']})"
        )

    response.append(
        "\nCategory distribution:"
    )

    category_order = [
        "Safe",
        "Semi-Critical",
        "Critical",
        "Over-Exploited",
        "Unknown"
    ]

    for category in category_order:

        count = distribution.get(
            category,
            0
        )

        response.append(
            f"• {category}: {count}"
        )

    return "\n".join(response)


# --------------------------------------------------
# MULTI-FIELD STATE RESPONSE
# --------------------------------------------------

def generate_multi_field_response(
    result,
    state=None,
    original_query=None
):

    if result is None or result.empty:
        return (
            "No groundwater data was found."
        )

    query = (
        original_query.lower()
        if original_query
        else ""
    )

    response = []

    response.append(
        f"Groundwater analysis for {state}"
    )

    # ----------------------------------------------
    # EXTRACTION
    # ----------------------------------------------

    wants_extraction = (
        "extract" in query
        or "extraction" in query
        or "exploitation" in query
    )

    if (
        wants_extraction
        and
        "Stage_of_Ground_Water_Extraction_pct"
        in result.columns
    ):

        response.append(
            "\nTop districts by groundwater extraction:"
        )

        for _, row in result.head(5).iterrows():

            district = row["DISTRICT"]

            extraction = row[
                "Stage_of_Ground_Water_Extraction_pct"
            ]

            category = row.get(
                "Extraction_Category",
                ""
            )

            response.append(
                f"• {district} — "
                f"{format_number(extraction)}%"
                f" ({category})"
            )

    # ----------------------------------------------
    # RAINFALL
    # ----------------------------------------------

    wants_rainfall = (
        "rainfall" in query
        or "rainfal" in query
    )

    if (
        wants_rainfall
        and "Rainfall_mm" in result.columns
    ):

        response.append(
            "\nRainfall:"
        )

        for _, row in result.head(5).iterrows():

            district = row["DISTRICT"]

            rainfall = row["Rainfall_mm"]

            response.append(
                f"• {district} — "
                f"{format_number(rainfall)} mm"
            )

    # ----------------------------------------------
    # RECHARGE
    # ----------------------------------------------

    wants_recharge = (
        "recharge" in query
        or "recharg" in query
    )

    if (
        wants_recharge
        and
        "Annual_Ground_Water_Recharge_ham"
        in result.columns
    ):

        response.append(
            "\nAnnual groundwater recharge:"
        )

        for _, row in result.head(5).iterrows():

            district = row["DISTRICT"]

            recharge = row[
                "Annual_Ground_Water_Recharge_ham"
            ]

            response.append(
                f"• {district} — "
                f"{format_integer_number(recharge)} ham"
            )

    if len(response) == 1:

        response.append(
            "\nNo specific structured field "
            "was identified in the query."
        )

    return "\n".join(response)


# --------------------------------------------------
# MAIN RESPONSE FUNCTION
# --------------------------------------------------

def generate_response(
    intent,
    analysis,
    state=None,
    district=None,
    structured_result=None,
    original_query=None
):

    # ----------------------------------------------
    # NO DATA
    # ----------------------------------------------

    if (
        structured_result is None
        or structured_result.empty
    ):

        if district:
            return generate_district_response(
                analysis,
                state,
                district
            )

        if state:
            return generate_state_analysis_response(
                analysis,
                state
            )

        return (
            "No groundwater data was found "
            "for the requested query."
        )

    query_text = (
        original_query.lower()
        if original_query
        else ""
    )

    # ----------------------------------------------
    # DISTRICT QUERY
    # ----------------------------------------------

    if district:

        has_rainfall = (
            "rainfall" in query_text
            or "rainfal" in query_text
        )

        has_recharge = (
            "recharge" in query_text
            or "recharg" in query_text
        )

        # Use field-specific response when the
        # user explicitly asks rainfall/recharge.

        if has_rainfall or has_recharge:

            return generate_district_field_response(
                structured_result,
                state=state,
                district=district,
                original_query=original_query
            )

        # Otherwise use the normal extraction
        # response.

        return generate_district_response(
            analysis,
            state,
            district
        )

    # ----------------------------------------------
    # STATE QUERY
    # ----------------------------------------------

    if state:

        has_rainfall = (
            "rainfall" in query_text
            or "rainfal" in query_text
        )

        has_recharge = (
            "recharge" in query_text
            or "recharg" in query_text
        )

        if has_rainfall or has_recharge:

            return generate_multi_field_response(
                structured_result,
                state=state,
                original_query=original_query
            )

        return generate_state_analysis_response(
            analysis,
            state
        )

    # ----------------------------------------------
    # NO LOCATION
    # ----------------------------------------------

    return (
        "The query was processed, "
        "but no location was identified."
    )