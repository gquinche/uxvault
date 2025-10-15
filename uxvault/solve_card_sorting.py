import streamlit as st
from datetime import datetime
from streamlit_kanban_os import kanban_board
import streamlit_kanban_os

def initialize_session_state():
    """Initialize base session state variables"""
    if "testing_survey" not in st.session_state:
        st.session_state.testing_survey = None
    if "sorted_cards" not in st.session_state:
        st.session_state.sorted_cards = None
    if "last_survey_config_hash" not in st.session_state:
        st.session_state.last_survey_config_hash = None

def initialize_card_sorting(survey_config):
    """Initialize or reset card sorting based on survey configuration"""
    # Create a hash of the current survey configuration
    current_config_hash = hash(str({
        "cards": survey_config["cards"],
        "use_named_categories": survey_config["use_named_categories"],
        "categories": survey_config.get("categories", []),
        "num_categories": survey_config.get("num_categories", 0)
    }))

    # Only reinitialize if this is a new survey or the config has changed
    if (not st.session_state.sorted_cards or 
        current_config_hash != st.session_state.last_survey_config_hash):
        st.session_state.sorted_cards = {
            "Uncategorized": survey_config["cards"].copy()
        }
        if survey_config["use_named_categories"]:
            for category in survey_config["categories"]:
                st.session_state.sorted_cards[category] = []
        else:
            for i in range(survey_config["num_categories"]):
                st.session_state.sorted_cards[f"Category {i+1}"] = []
        
        # Store the current config hash for future comparisons
        st.session_state.last_survey_config_hash = current_config_hash

def render_header(survey_config):
    """Render the survey header with title and description"""
    with st.container(horizontal=True):
        if survey_config.get("title"):
            st.title(survey_config["title"])
        else:
            st.title("Card Sorting Survey")

        board_layout = st.pills(
            "Interface",
            options=["Legacy Standard", "Desktop", "Mobile"],
            default="Desktop",
            help="Legacy Standard: Traditional interface | Desktop: Standard kanban | Mobile: Stacked layout (recommended for mobile devices)"
        )

    if survey_config["description"]:
        st.write(survey_config["description"])
    else:
        st.write("Please select a category for each card below")
    st.divider()

    return board_layout

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

# LEGACY FUNCTIONS - Keep as backup for traditional card sorting interface
def render_card(card: str, current_category: str, categories: list[str]):
    """Render a single card with its move options"""
    # Simple container with card and move options
    with st.container():
        st.write(card)
        # Include current category and others
        move_options = [current_category] + [cat for cat in categories if cat != current_category]
        
        # Initialize session state with current category if not set
        if f"move_{card}" not in st.session_state:
            st.session_state[f"move_{card}"] = current_category
        
        # Choose between radio and select based on number of options
        if len(move_options) <= 3:  # Include current category in count
            st.radio(
                "Move to category:",
                options=move_options,
                key=f"move_{card}",
                horizontal=True,
                on_change=move_card,
                args=(card, current_category, f"move_{card}"),
                label_visibility="collapsed",
                index=0  # Current category is first
            )
        else:
            st.selectbox(
                "Move to category:",
                options=move_options,
                key=f"move_{card}",
                on_change=move_card,
                args=(card, current_category, f"move_{card}"),
                label_visibility="collapsed",
                index=0  # Current category is first
            )

def move_card(card: str, from_category: str, move_key: str):
    """Move card between categories"""
    to_category = st.session_state[move_key]
    if to_category != from_category:
        st.session_state.sorted_cards[from_category].remove(card)
        st.session_state.sorted_cards[to_category].append(card)

def render_kanban_interface(survey_config, board_layout):
    """Render the kanban board interface for card sorting"""
    # Use default gap since we removed the control
    gap = "medium"

    # Build initial board structure for kanban
    initial_board = []
    card_id_counter = 1

    for category, cards in st.session_state.sorted_cards.items():
        cards_as_dicts = []
        for card_title in cards:
            card_dict = {"id": str(card_id_counter), "title": card_title}
            cards_as_dicts.append(card_dict)
            card_id_counter += 1

        column_dict = {
            "title": category,
            "cards": cards_as_dicts
        }

        # Set "Uncategorized" as main column
        if category == "Uncategorized":
            column_dict["is_main_column"] = True
        else:
            column_dict["is_main_column"] = False

        initial_board.append(column_dict)

    # Generate unique key for the kanban board
    component_key = f"kanban_{hash(str(initial_board))}"

    # Choose interface based on selection
    if board_layout == "Legacy Standard":
        # Use legacy card sorting interface
        for category, cards in st.session_state.sorted_cards.items():
            with st.container(border=True):
                st.subheader(category)
                if cards:
                    with st.container(horizontal=True, gap="small"):
                        for card in cards:
                            render_card(card, category, list(st.session_state.sorted_cards.keys()))
                else:
                    st.caption("No cards in this category")
        return None  # Legacy interface doesn't return board state
    else:
        # Determine stacked mode based on board_layout
        if board_layout == "Desktop":
            is_stacked = False
            horizontal_alignment = "left"
        else:  # Mobile
            is_stacked = True
            horizontal_alignment = "center"

        # Set default minHeight and check for override in config
        default_min_height = 100  # Default minimum height in pixels
        min_height = survey_config.get("min_height", default_min_height)

        # Render the kanban board
        board_state = kanban_board(
            initial_board,
            horizontal=True,  # Horizontal layout by default
            horizontal_alignment=horizontal_alignment,
            gap=gap,
            width="stretch",
            height="content",
            stacked=is_stacked,
            main_column_min_width="stretch",
            min_width=200,  # Minimum width to prevent resizing
            min_height=min_height,
            key=component_key,
            
        )

    # Board state is available for processing if needed
    # Debug output removed for clean user interface

    # For now, return the board_state as-is without processing
    # TODO: Implement proper board_state processing once we understand the format
    return board_state


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

def get_example_survey():
    """Returns an example card sorting survey configuration"""
    return {
        "title": "Example Card Sorting Survey",
        "description": "This is an example survey to help you understand how card sorting works.",
        "cards": [
            "Online Banking",
            "ATM Locations",
            "Credit Cards",
            "Mortgage Calculator",
            "Investment Portfolio",
            "Savings Account",
            "Foreign Exchange",
            "Wire Transfer",
            "Mobile Banking App",
            "Customer Support"
        ],
        "use_named_categories": True,
        "categories": [
            "Account Services",
            "Tools & Calculators",
            "Banking Channels",
            "Support"
        ],
        "allow_custom_categories": True
    }

def main():
    # Initialize base session state
    initialize_session_state()
    
    # Handle no active survey case
    if not st.session_state.testing_survey:
        with st.container():
            st.error("No survey configuration found. Please create a survey first.")
            
            with st.container(horizontal=True, gap="medium"):
                if st.button("Back to Survey Creation"):
                    st.switch_page("uxvault/create_card_sorting.py")
                if st.button("Try Example Survey"):
                    st.session_state.testing_survey = get_example_survey()
                    st.rerun()
        st.stop()
    
    # Initialize card sorting if needed
    survey_config = st.session_state.testing_survey
    initialize_card_sorting(survey_config)
    
    board_layout = render_header(survey_config)

    if survey_config["allow_custom_categories"]:
        render_category_creator()

    render_kanban_interface(survey_config, board_layout)
    
    if handle_completion():
        results = {
            "survey_config": survey_config,
            "sorted_cards": st.session_state.sorted_cards,
            "completed_at": str(datetime.now())
        }
        # st.json(results)

if __name__ == "__main__":
    main()
