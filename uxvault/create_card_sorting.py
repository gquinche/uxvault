import streamlit as st

with st.container(horizontal=False, gap="medium", horizontal_alignment="center"):
    # Capture all inputs in variables
    survey_title = st.text_input("Survey Title", placeholder="Card Sorting Survey", width=300, key="survey_title")
    allow_custom = st.pills(
        label="Allow users to create their own categories",
        options=["Yes", "No"],
        default="No",
        width=300,
        help="An open card sorting allows participants to create their own categories," \
             " while a closed card sorting provides predefined categories for them to sort into.",
        key="allow_custom_categories"
    )
    survey_description = st.text_area(
        "Description", 
        placeholder="Optional extra description here...", 
        width=300,
        key="survey_description"
    )
    cards = st.multiselect(
        "Write down the cards to include in the survey",
        options=["Example card 1", "Example card 2", "Example card 3"],
        width=300,
        help="These are the objects the user will sort into categories.",
        accept_new_options=True,
        key="cards"
    )
    
    use_named_categories = st.pills(
        "Use named categories",
        options=["Yes", "No"],
        default="No",
        width=300,
        help="If you select 'No' categories won't have any names.",
        key="use_named_categories"
    )

    # Initialize categories variable
    categories = None
    num_categories = None
    
    if use_named_categories == "Yes":
        categories = st.multiselect(
            "Write down the categories to include in the survey",
            options=["Example category 1", "Example category 2", "Example category 3"],
            width=300,
            help="These are the categories the user will sort into.",
            accept_new_options=True,
            key="named_categories"
        )
    else:
        num_categories = st.number_input(
            "Number of categories", 
            min_value=2, 
            max_value=20, 
            step=1, 
            value=5,
            help="This is the number of categories the user will sort the cards into.",
            width=300,
            key="num_categories"
        )

    # Create survey configuration dictionary
    survey_config = {
        "title": survey_title,
        "description": survey_description,
        "allow_custom_categories": allow_custom == "Yes",
        "cards": cards,
        "use_named_categories": use_named_categories == "Yes",
        "categories": categories if categories else [],
        "num_categories": num_categories if num_categories else 0,
        "created_at": str(st.session_state.get("created_at", "")),
        "updated_at": str(st.session_state.get("updated_at", ""))
    }

    if st.button("Test Survey", type="secondary", width=300,
                 help="This will allow you to test the card sorting survey with the provided details."):
        st.success("Testing survey...")
        st.write("Survey Configuration:")
        # st.json(survey_config)
        st.session_state["testing_survey"] = survey_config
        st.switch_page("uxvault/solve_card_sorting.py")

    if st.button("Create Survey", type="primary", width=300,
                 help="This will create the card sorting survey with the provided details."):
        st.success("Creating survey...")
        # Here you can save survey_config to a file or database
        st.json(survey_config)
