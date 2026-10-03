import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


# ---------------------------------------------------------
# INGRES - Module 2
# Query Processing
# ---------------------------------------------------------

# Initialize NLP tools
STOP_WORDS = set(stopwords.words("english"))
STEMMER = PorterStemmer()


def tokenize(query):
    """
    Convert the input query into individual tokens.
    """

    if not isinstance(query, str):
        raise TypeError("Query must be a string.")

    tokens = re.findall(r"[A-Za-z0-9]+", query)

    return tokens


def lowercase(tokens):
    """
    Convert all tokens to lowercase.
    """

    return [
        token.lower()
        for token in tokens
    ]


def remove_stopwords(tokens):
    """
    Remove common English stop words.
    """

    return [
        token
        for token in tokens
        if token not in STOP_WORDS
    ]


def stem_tokens(tokens):
    """
    Apply Porter Stemming to each token.
    """

    return [
        STEMMER.stem(token)
        for token in tokens
    ]


def normalize_query(query):
    """
    Complete query-processing pipeline.

    Query
       ↓
    Tokenization
       ↓
    Lowercasing
       ↓
    Stop-word Removal
       ↓
    Stemming
       ↓
    Normalized Query
    """

    # Step 1: Tokenization
    tokens = tokenize(query)

    # Step 2: Lowercasing
    lowercase_tokens = lowercase(tokens)

    # Step 3: Stop-word removal
    filtered_tokens = remove_stopwords(
        lowercase_tokens
    )

    # Step 4: Stemming
    normalized_tokens = stem_tokens(
        filtered_tokens
    )

    # Step 5: Convert normalized tokens
    # into a single searchable string
    normalized_text = " ".join(
        normalized_tokens
    )

    return {
        "original_query": query,
        "tokens": tokens,
        "lowercase_tokens": lowercase_tokens,
        "filtered_tokens": filtered_tokens,
        "normalized_tokens": normalized_tokens,
        "normalized_text": normalized_text
    }


def get_normalized_query(query):
    """
    Return only the normalized query representation.

    This function will be useful for later modules.
    """

    result = normalize_query(query)

    return {
        "original_query": result["original_query"],
        "normalized_tokens": result["normalized_tokens"],
        "normalized_text": result["normalized_text"]
    }


def main():

    print("----- INGRES Module 2: Query Processing -----")

    query = input("\nEnter your query: ")

    result = normalize_query(query)

    print("\nOriginal Query:")
    print(result["original_query"])

    print("\nTokens:")
    print(result["tokens"])

    print("\nLowercase Tokens:")
    print(result["lowercase_tokens"])

    print("\nAfter Stop-word Removal:")
    print(result["filtered_tokens"])

    print("\nAfter Stemming:")
    print(result["normalized_tokens"])

    print("\nNormalized Query:")
    print(result["normalized_text"])

    print("\n----- Query Processing Successful -----")


if __name__ == "__main__":
    main()