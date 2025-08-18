import streamlit as st
from datetime import datetime

def initialize_session_state(survey_config):
    """Initialize session state variables for the card sorting"""
    if "sorted_cards" not in st.session_state: #fix bug that stores previous card sorting
        st.session_state.sorted_cards = {
            "Uncategorized": survey_config["cards"].copy()
        }
        if survey_config["use_named_categories"]:
            for category in survey_config["categories"]:
                st.session_state.sorted_cards[category] = []
        else:
            for i in range(survey_config["num_categories"]):
                st.session_state.sorted_cards[f"Category {i+1}"] = []

def render_header(survey_config):
    """Render the survey header with title and description"""
    if survey_config.get("title"):
        st.title(survey_config["title"])
    else:
        st.title("Card Sorting Survey")
    if survey_config["description"]:
        st.write(survey_config["description"])
    else:
        st.write("Please select a category for each card below")
    st.divider()

def render_category_creator():
    """Render the interface for creating new categories"""
    st.text("If none of the categories seem to fit the class create new ones here")
    with st.container(horizontal=True):
        new_category = st.text_input(
            "Create new category",
            key="new_category_input",
            placeholder="New Category name",
            label_visibility="collapsed",
        )
        if st.button("Add", key="add_category_button"):
            if new_category and new_category not in st.session_state.sorted_cards:
                st.session_state.sorted_cards[new_category] = []
                st.success(f"Added category: {new_category}")
                st.rerun()
    st.divider()

def render_card(card: str, current_category: str, categories: list[str]):
    """Render a single card with its move options"""
    # Simple container with card and move options
    with st.container():
        st.write(card)
        other_categories = [cat for cat in categories if cat != current_category]
        
        # Choose between radio and select based on number of options
        if len(other_categories) <= 2:
            st.radio(
                "Move to category:",
                options=other_categories,
                key=f"move_{card}",
                horizontal=True,
                on_change=move_card,
                args=(card, current_category, f"move_{card}"),
                label_visibility="collapsed"
            )
        else:
            st.selectbox(
                "Move to category:",
                options=other_categories,
                key=f"move_{card}",
                on_change=move_card,
                args=(card, current_category, f"move_{card}"),
                label_visibility="collapsed"
            )

def move_card(card: str, from_category: str, move_key: str):
    """Move card between categories"""
    to_category = st.session_state[move_key]
    if to_category != from_category:
        st.session_state.sorted_cards[from_category].remove(card)
        st.session_state.sorted_cards[to_category].append(card)

def render_card_sorting_interface():
    """Render the main card sorting interface"""
    for category, cards in st.session_state.sorted_cards.items():
        with st.container(border=True):
            st.subheader(category)
            if cards:
                with st.container(horizontal=True, gap="small"):
                    for card in cards:
                        render_card(card, category, list(st.session_state.sorted_cards.keys()))
            else:
                st.caption("No cards in this category")


def check_completition():
    if st.session_state.sorted_cards.get("Uncategorized"):
        st.warning("Please categorize all cards before completing.")
        return False
    else:
        # st.empty()
        # force a new line with some empty content
        st.divider()
        st.success("Card sorting completed!")
        return True

def handle_completion():
    """Handle the completion of card sorting"""
    container = st.container(horizontal=True, gap="medium", horizontal_alignment="right")

    if container.button("Reset", type="secondary"):
        st.session_state.pop("sorted_cards")
        st.rerun()
    if container.button("Complete", type="primary"):
        return check_completition()
    return False

def main():
    if "testing_survey" not in st.session_state:
        st.error("No survey configuration found. Please create a survey first.")
        if st.button("Back to Survey Creation"):
            st.switch_page("uxvault/create_card_sorting.py")
        st.stop()
    
    survey_config = st.session_state["testing_survey"]
    initialize_session_state(survey_config)
    render_header(survey_config)
    
    if survey_config["allow_custom_categories"]:
        render_category_creator()
    
    render_card_sorting_interface()
    
    if handle_completion():
        results = {
            "survey_config": survey_config,
            "sorted_cards": st.session_state.sorted_cards,
            "completed_at": str(datetime.now())
        }
        st.json(results)

if __name__ == "__main__":
    main()
