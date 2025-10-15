import streamlit as st
from datetime import datetime
import sys
import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uxvault.utils.url_handling import get_share_url

MAX_WIDTH = 'stretch'

def render_share_options(survey_config: dict):
    """Render sharing options for the survey"""
    with st.container():
        use_base64 = st.toggle(
            "Encode survey data",
            help="Enable to encode survey data in URL (recommended for privacy)",
            value=True
        )
        
        share_url = get_share_url(survey_config, use_base64)
        st.code(share_url, language=None)
        
        with st.expander("Preview Configuration"):
            st.json(survey_config)
            
def validate_survey_config() -> bool:
    """
    Validate the survey configuration before creation.
    Returns True if valid, False if invalid (shows error messages for invalid cases)
    """
    is_valid = True
    errors = []
    
    # Check title
    if not st.session_state.get("survey_title"):
        errors.append("Survey title is required")
    
    # Check cards
    cards = st.session_state.get("cards", [])
    if not cards:
        errors.append("At least one card is required")
    if len(cards) < 2:
        errors.append("At least two cards are needed for sorting")
    if len(cards) != len(set(cards)):
        errors.append("Duplicate cards are not allowed")
    
    # Check categories based on configuration
    if st.session_state.get("use_named_categories") == "Yes":
        categories = st.session_state.get("named_categories", [])
        if not categories:
            errors.append("At least one category is required when using named categories")
        if len(categories) < 2:
            errors.append("At least two categories are needed for sorting")
        if len(categories) != len(set(categories)):
            errors.append("Duplicate categories are not allowed")
            
        # Check if categories are not just whitespace
        if any(not cat.strip() for cat in categories):
            errors.append("Categories cannot be empty or just whitespace")
    else:
        num_categories = st.session_state.get("num_categories", 0)
        if num_categories < 2:
            errors.append("At least two categories are required")
        if num_categories > 20:  # Reasonable upper limit
            errors.append("Too many categories (maximum is 20)")
    
    # Validate card content
    for card in cards:
        if not card.strip():
            errors.append("Cards cannot be empty or just whitespace")
            break
            
    # Optional: validate description length
    description = st.session_state.get("survey_description", "")
    if len(description) > 500:  # Reasonable limit
        errors.append("Description is too long (maximum 500 characters)")
    
    # Display all errors if any
    if errors:
        with st.container():
            st.error("Please fix the following errors:")
            for error in errors:
                st.write(f"• {error}")
        is_valid = False
    
    return is_valid

with st.container(horizontal=False, gap="medium", horizontal_alignment="center"):
    # Capture all inputs in variables
    survey_title = st.text_input("Survey Title", placeholder="Card Sorting Survey", width=MAX_WIDTH, key="survey_title")
    allow_custom = st.pills(
        label="Allow users to create their own categories",
        options=["Yes", "No"],
        default="No",
        width=MAX_WIDTH,
        help="An open card sorting allows participants to create their own categories," \
             " while a closed card sorting provides predefined categories for them to sort into.",
        key="allow_custom_categories"
    )
    survey_description = st.text_area(
        "Description", 
        placeholder="Optional extra description here...", 
        width=MAX_WIDTH,
        key="survey_description"
    )
    cards = st.multiselect(
        "Write down the cards to include in the survey",
        options=["Example card 1", "Example card 2", "Example card 3"],
        width=MAX_WIDTH,
        help="These are the objects the user will sort into categories.",
        accept_new_options=True,
        key="cards"
    )
    
    use_named_categories = st.pills(
        "Use named categories",
        options=["Yes", "No"],
        default="No",
        width=MAX_WIDTH,
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
            width=MAX_WIDTH,
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
            width=MAX_WIDTH,
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

    if st.button("Test Survey", type="secondary", width=MAX_WIDTH,
                 help="This will allow you to test the card sorting survey with the provided details."):
        st.success("Testing survey...")
        st.write("Survey Configuration:")
        # st.json(survey_config)
        st.session_state["testing_survey"] = survey_config
        st.switch_page("uxvault/solve_card_sorting.py")

    if st.button("Create Survey", type="primary", width=MAX_WIDTH,
                 help="This will create the card sorting survey with the provided details."):
        if validate_survey_config():  # You'll need to implement this
            survey_config = {
                "title": st.session_state.survey_title,
                "description": st.session_state.survey_description,
                "cards": st.session_state.cards,
                "use_named_categories": st.session_state.use_named_categories == "Yes",
                "categories": st.session_state.get("named_categories", []),
                "num_categories": st.session_state.get("num_categories", 0),
                "allow_custom_categories": st.session_state.allow_custom_categories == "Yes",
                "created_at": str(datetime.now())
            }
            
            # Store in session state for testing
            st.session_state.testing_survey = survey_config
            
            # Show success message
            st.success("Survey created successfully!")
            
            # Show sharing options
            st.divider()
            st.subheader("Share Survey")
            render_share_options(survey_config)
            
            # Test button
            st.divider()
            if st.button("Test Survey", type="secondary", width=300):
                st.switch_page("uxvault/solve_card_sorting.py")
