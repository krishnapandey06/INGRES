import sys

sys.path.insert(0, "src")

from full_pipeline import run_full_pipeline


# --------------------------------------------------
# MODULE 8: CHATBOT / CONVERSATION
# --------------------------------------------------

def start_chatbot():

    print("================================================")
    print(" INGRES - GROUNDWATER CHATBOT")
    print("================================================")
    print("Ask questions about groundwater data.")
    print("The chatbot supports follow-up questions.")
    print("Type 'exit' or 'quit' to stop.")
    print("================================================")

    # --------------------------------------------------
    # CONVERSATION CONTEXT
    # --------------------------------------------------

    context = {
        "state": None,
        "district": None,
        "intent": None,
        "last_result_district": None,
        "last_query": None
    }

    while True:

        query = input("\nYou: ").strip()

        # --------------------------------------------------
        # EXIT
        # --------------------------------------------------

        if query.lower() in ["exit", "quit"]:

            print("\nINGRES: Goodbye!")
            break

        # --------------------------------------------------
        # EMPTY QUERY
        # --------------------------------------------------

        if not query:

            print(
                "\nINGRES: Please enter a question."
            )

            continue

        try:

            # --------------------------------------------------
            # FIRST PIPELINE RUN
            # --------------------------------------------------

            result = run_full_pipeline(query)

            analysis = result["analysis"]

            current_intent = analysis["intent"]
            current_states = analysis["states"]
            current_districts = analysis["districts"]

            # --------------------------------------------------
            # UPDATE STATE CONTEXT
            # --------------------------------------------------

            if current_states:

                new_state = current_states[0]

                # If user changes state,
                # remove the previous district.

                if (
                    context["state"] is not None
                    and new_state != context["state"]
                ):

                    context["district"] = None

                context["state"] = new_state

            # --------------------------------------------------
            # UPDATE DISTRICT CONTEXT
            # --------------------------------------------------

            if current_districts:

                context["district"] = (
                    current_districts[0]
                )

            # --------------------------------------------------
            # UPDATE INTENT
            # --------------------------------------------------

            if current_intent != "UNKNOWN":

                context["intent"] = (
                    current_intent
                )

            # --------------------------------------------------
            # DETERMINE WHETHER CONTEXT IS NEEDED
            # --------------------------------------------------

            needs_context = (
                not current_states
                or not current_districts
                or current_intent == "UNKNOWN"
            )

            # --------------------------------------------------
            # HANDLE FOLLOW-UP QUESTIONS
            # --------------------------------------------------

            if needs_context:

                state = context["state"]

                district = context["district"]

                previous_intent = (
                    context["intent"]
                )

                # ----------------------------------------------
                # DETERMINE FOLLOW-UP INTENT
                # ----------------------------------------------

                if previous_intent == (
                    "GROUNDWATER_STATUS"
                ):

                    contextual_query = (
                        "show groundwater status"
                    )

                elif previous_intent == (
                    "GROUNDWATER_EXTRACTION"
                ):

                    contextual_query = (
                        "show groundwater extraction"
                    )

                elif previous_intent == (
                    "RAINFALL"
                ):

                    contextual_query = (
                        "show rainfall"
                    )

                elif previous_intent == (
                    "GROUNDWATER_RECHARGE"
                ):

                    contextual_query = (
                        "show groundwater recharge"
                    )

                elif previous_intent == (
                    "EXTRACTION_STATUS"
                ):

                    contextual_query = (
                        "show groundwater status"
                    )

                else:

                    contextual_query = query

                # ----------------------------------------------
                # ADD DISTRICT
                # ----------------------------------------------

                if district:

                    contextual_query += (
                        f" {district}"
                    )

                # ----------------------------------------------
                # ADD STATE
                # ----------------------------------------------

                if state:

                    contextual_query += (
                        f" {state}"
                    )

                # ----------------------------------------------
                # RUN CONTEXTUAL QUERY
                # ----------------------------------------------

                if contextual_query != query:

                    result = run_full_pipeline(
                        contextual_query
                    )

                    analysis = result[
                        "analysis"
                    ]

            # --------------------------------------------------
            # UPDATE CONTEXT AFTER CONTEXTUAL QUERY
            # --------------------------------------------------

            if analysis["states"]:

                context["state"] = (
                    analysis["states"][0]
                )

            if analysis["districts"]:

                context["district"] = (
                    analysis["districts"][0]
                )

            if analysis["intent"] != "UNKNOWN":

                context["intent"] = (
                    analysis["intent"]
                )

            # --------------------------------------------------
            # STORE LAST RESULT DISTRICT
            # --------------------------------------------------

            if analysis.get("districts"):

                context[
                    "last_result_district"
                ] = analysis["districts"][0]

            else:

                data_analysis = result.get(
                    "data_analysis",
                    {}
                )

                highest = data_analysis.get(
                    "highest_extraction"
                )

                if highest:

                    context[
                        "last_result_district"
                    ] = highest["district"]

            # --------------------------------------------------
            # STORE LAST QUERY
            # --------------------------------------------------

            context["last_query"] = query

            # --------------------------------------------------
            # FINAL RESPONSE
            # --------------------------------------------------

            response = result[
                "response"
            ]

            print("\nINGRES:")
            print(response)

            # --------------------------------------------------
            # CONVERSATION CONTEXT
            # --------------------------------------------------

            print(
                "\n[Conversation Context]"
            )

            print(
                f"Intent: "
                f"{context['intent']}"
            )

            print(
                f"State: "
                f"{context['state']}"
            )

            print(
                f"District: "
                f"{context['district']}"
            )

            print(
                f"Last Result District: "
                f"{context['last_result_district']}"
            )

        except Exception as e:

            print(
                "\nINGRES: Sorry, I could not "
                "process that query."
            )

            print(
                f"Error: {e}"
            )


# --------------------------------------------------
# PROGRAM ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":

    start_chatbot()