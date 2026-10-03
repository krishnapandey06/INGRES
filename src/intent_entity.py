import os
import pandas as pd
from nltk.stem import PorterStemmer

STEMMER = PorterStemmer()

# --------------------------------------------------
# PATHS
# --------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

CSV_PATH = os.path.join(
    BASE_DIR,
    "data",
    "INGRES_Step1_Cleaned_Dataset.csv"
)


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

df = pd.read_csv(CSV_PATH)

STATE_VALUES = sorted(
    df["STATE"].dropna().astype(str).unique(),
    key=len,
    reverse=True
)

DISTRICT_VALUES = sorted(
    df["DISTRICT"].dropna().astype(str).unique(),
    key=len,
    reverse=True
)


# --------------------------------------------------
# INTENT DETECTION
# --------------------------------------------------

def detect_intent(query):

    query = str(query).lower()

    # Groundwater extraction
    if (
        "extract" in query
        and (
            "percent" in query
            or "stage" in query
            or "groundwat" in query
        )
    ):
        return "GROUNDWATER_EXTRACTION"

    # Rainfall
    if "rain" in query:
        return "RAINFALL"

    # Groundwater recharge
    if (
        "recharg" in query
        or "replenish" in query
    ):
        return "GROUNDWATER_RECHARGE"

    # Extraction status
    if (
        "over" in query
        and "exploit" in query
    ):
        return "EXTRACTION_STATUS"

    # Groundwater status
    if (
        (
            "status" in query
            or "statu" in query
        )
        and "groundwat" in query
    ):
        return "GROUNDWATER_STATUS"

    return "UNKNOWN"


# --------------------------------------------------
# ENTITY MATCHING
# --------------------------------------------------

def entity_matches_query(entity, query):

    entity = str(entity).lower().strip()
    query = str(query).lower().strip()

    # Remove punctuation
    entity = "".join(
        ch if ch.isalnum() or ch == " " else " "
        for ch in entity
    )

    query = "".join(
        ch if ch.isalnum() or ch == " " else " "
        for ch in query
    )

    entity_words = entity.split()
    query_words = query.split()

    # ------------------------------------------------
    # 1. NORMAL EXACT MATCH
    # ------------------------------------------------

    if len(entity_words) <= len(query_words):

        for i in range(
            len(query_words) - len(entity_words) + 1
        ):

            query_section = query_words[
                i:i + len(entity_words)
            ]

            if query_section == entity_words:
                return True

    # ------------------------------------------------
    # 2. COMPACT MATCH
    #
    # Tamilnadu <-> Tamil Nadu
    # ------------------------------------------------

    entity_compact = "".join(entity_words)

    for start in range(len(query_words)):

        combined = ""

        for end in range(
            start,
            len(query_words)
        ):

            combined += query_words[end]

            if combined == entity_compact:
                return True

            if len(combined) >= len(entity_compact):
                break

    # ------------------------------------------------
    # 3. STEMMED ENTITY MATCH
    #
    # Jaisalmer -> jaisalm
    # ------------------------------------------------

    entity_stems = [
        STEMMER.stem(word)
        for word in entity_words
    ]

    query_stems = [
        STEMMER.stem(word)
        for word in query_words
    ]

    if len(entity_stems) <= len(query_stems):

        for i in range(
            len(query_stems) - len(entity_stems) + 1
        ):

            query_section = query_stems[
                i:i + len(entity_stems)
            ]

            if query_section == entity_stems:
                return True

    # ------------------------------------------------
    # 4. STEMMED COMPACT MATCH
    #
    # Handles multi-word entities after stemming
    # ------------------------------------------------

    entity_stem_compact = "".join(entity_stems)

    for start in range(len(query_stems)):

        combined = ""

        for end in range(
            start,
            len(query_stems)
        ):

            combined += query_stems[end]

            if combined == entity_stem_compact:
                return True

            if len(combined) >= len(
                entity_stem_compact
            ):
                break

    return False

# --------------------------------------------------
# ENTITY DETECTION
# --------------------------------------------------

def detect_entities(query):

    detected_states = []
    detected_districts = []

    # -----------------------------
    # STATES
    # -----------------------------

    for state in STATE_VALUES:

        if entity_matches_query(
            state,
            query
        ):
            detected_states.append(state)

    # -----------------------------
    # DISTRICTS
    # -----------------------------

    for district in DISTRICT_VALUES:

        if entity_matches_query(
            district,
            query
        ):
            detected_districts.append(district)

    return {
        "states": detected_states,
        "districts": detected_districts
    }


# --------------------------------------------------
# COMPLETE ANALYSIS
# --------------------------------------------------

def analyze_query(query):

    intent = detect_intent(query)

    entities = detect_entities(query)

    return {
        "query": query,
        "intent": intent,
        "states": entities["states"],
        "districts": entities["districts"]
    }


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print(
        "----- INGRES Module 3: "
        "Intent & Entity Detection -----"
    )

    query = input(
        "\nEnter normalized query: "
    )

    result = analyze_query(query)

    print("\nNormalized Query:")
    print(result["query"])

    print("\nDetected Intent:")
    print(result["intent"])

    print("\nDetected Entities:")

    print("States:")
    print(result["states"])

    print("Districts:")
    print(result["districts"])

    print(
        "\n----- Module 3 Analysis Successful -----"
    )


if __name__ == "__main__":
    main()