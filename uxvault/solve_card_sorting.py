import streamlit as st
from datetime import datetime

def initialize_session_state(survey_config):
    """Initialize session state variables for the card sorting"""
    if "sorted_cards" not in st.session_state: #fix bug that stores previous card sorting
        st.session_state.sorted_cards = {
            "uncategorized": survey_config["cards"].copy()
        }
        if survey_config["use_named_categories"]:
            for category in survey_config["categories"]:
                st.session_state.sorted_cards[category] = []
        else:
            for i in range(survey_config["num_categories"]):
                st.session_state.sorted_cards[f"Category {i+1}"] = []

def render_header(survey_config):
    """Render the survey header with title and description"""
    st.title(survey_config["title"])
    if survey_config["description"]:
        st.write(survey_config["description"])
    st.divider()

def render_category_creator():
    """Render the interface for creating new categories"""
    with st.container(horizontal=True):
        new_category = st.text_input(
            "Create new category",
            key="new_category_input",
            placeholder="Enter category name...",
            label_visibility="collapsed"
        )
        if st.button("Add Category", key="add_category_button"):
            if new_category and new_category not in st.session_state.sorted_cards:
                st.session_state.sorted_cards[new_category] = []
                st.success(f"Added category: {new_category}")
                st.rerun()

def render_card_sorting_interface():
    """Render the main card sorting interface"""
    cols = st.columns(len(st.session_state.sorted_cards))
    
    for col, (category, cards) in zip(cols, st.session_state.sorted_cards.items()):
        with col:
            st.subheader(category)
            for card in cards:
                # Create a container for each card with move options
                with st.container():
                    st.write(card)
                    move_to = st.selectbox(
                        "Move to",
                        options=[cat for cat in st.session_state.sorted_cards.keys() 
                               if cat != category],
                        key=f"move_{card}_{category}",
                        label_visibility="collapsed"
                    )
                    if st.button("Move", key=f"move_button_{card}_{category}"):
                        # Move card to selected category
                        st.session_state.sorted_cards[category].remove(card)
                        st.session_state.sorted_cards[move_to].append(card)
                        st.rerun()

def main():
    if "testing_survey" not in st.session_state:
        st.error("No survey configuration found. Please create a survey first.")
        if st.button("Go back to survey creation"):
            st.switch_page("uxvault/create_card_sorting.py")
        st.stop()
    
    survey_config = st.session_state["testing_survey"]
    initialize_session_state(survey_config)
    render_header(survey_config)
    
    if survey_config["allow_custom_categories"]:
        render_category_creator()
    
    render_card_sorting_interface()
    
    # Add completion button
    if st.button("Complete Sorting", type="primary"):
        st.success("Card sorting completed!")
        # Save results
        results = {
            "survey_config": survey_config,
            "sorted_cards": st.session_state.sorted_cards,
            "completed_at": str(datetime.now())
        }
        st.json(results)
        
    # Add reset button
    if st.button("Reset Sorting", type="secondary"):
        st.session_state.pop("sorted_cards")
        st.rerun()

if __name__ == "__main__":
    main()
