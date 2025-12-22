import streamlit as st
from datetime import datetime
import time as time
from streamlit_kanban_os import kanban_board
import streamlit_kanban_os
# from uxvault.utils.url_handling import get_survey_id_from_url # Import for URL handling
import uxvault.backend.supabase_client as supabase_client
import importlib

importlib.reload(supabase_client)
# TODO use an st.fragment to control for reruns of the kanban board to reduce complexity of code
test_survey_uuid = 'bd9550c7-e11c-4df5-87e9-cd57744c7d21'
def initialize_session_state():
    """Initialize base session state variables"""
    if "testing_survey" not in st.session_state:
        st.session_state.testing_survey = None
    if "sorted_cards" not in st.session_state:
        st.session_state.sorted_cards = None
    if "card_sorting_reset" not in st.session_state:
        st.session_state.card_sorting_reset = True
    if "completion_state" not in st.session_state:
        st.session_state.completion_state = None  # Stores completion status and message
    if "completion_message" not in st.session_state:
        st.session_state.completion_message = None  # Stores the message to display

def initialize_card_sorting(survey_config):
    """Initialize or reset card sorting based on survey configuration"""
    # Reset card sorting if the reset flag is set (new survey or manual reset)
    if not st.session_state.sorted_cards or st.session_state.card_sorting_reset:
        # Initialize with empty dictionary if not exists
        if not st.session_state.sorted_cards:
            st.session_state.sorted_cards = {}
        
        # Preserve existing categories but ensure Uncategorized exists with cards
        if "Uncategorized" not in st.session_state.sorted_cards:
            st.session_state.sorted_cards["Uncategorized"] = survey_config["cards"].copy()

        # Always load predefined categories if they exist (for any card sorting type)
        categories = survey_config.get("categories", [])
        for category in categories:
            if category not in st.session_state.sorted_cards:
                st.session_state.sorted_cards[category] = []

        # Clear the reset flag after initialization
        st.session_state.card_sorting_reset = False

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

def sync_board_state():
    """Synchronize board state with sorted_cards"""
    if getattr(st.session_state, 'last_board_state', None):
        try:
            import json
            board_data = st.session_state.last_board_state
            if isinstance(board_data, str):
                board_data = json.loads(board_data)

            if isinstance(board_data, dict) and "columns" in board_data:
                # Update sorted_cards to match board state
                st.session_state.sorted_cards = {}
                for column in board_data["columns"]:
                    st.session_state.sorted_cards[column["title"]] = [card["title"] for card in column["cards"]]
        except Exception as e:
            st.error(f"Error syncing board state: {str(e)}")

def add_category_to_board_state(category_name):
    """Helper function to add a category to the cached board state"""
    if getattr(st.session_state, 'last_board_state', None):
        try:
            import json
            board_data = st.session_state.last_board_state
            if isinstance(board_data, str):
                board_data = json.loads(board_data)

            if isinstance(board_data, dict) and "columns" in board_data:
                # Update board state
                board_data["columns"].append({"title": category_name, "cards": []})
                st.session_state.last_board_state = board_data
                sync_board_state()
        except Exception as e:
            st.error(f"Error adding category: {str(e)}")

def add_quick_category():
    """Callback to add a new category with auto-generated name"""
    # Get existing categories from cached board state
    existing_categories = []
    if hasattr(st.session_state, 'last_board_state'):
        try:
            import json
            if isinstance(st.session_state.last_board_state, str):
                board_data = json.loads(st.session_state.last_board_state)
            else:
                board_data = st.session_state.last_board_state

            if isinstance(board_data, dict) and "columns" in board_data:
                existing_categories = [col.get("title", "") for col in board_data.get("columns", [])]
        except:
            existing_categories = []

    # Generate unique default category name
    base_name = "New Category"
    counter = 1
    category_name = base_name
    while category_name in existing_categories:
        counter += 1
        category_name = f"{base_name} {counter}"

    # Add category and sync state
    add_category_to_board_state(category_name)

def add_custom_category():
    """Callback to add a custom named category"""
    new_category = st.session_state.get("new_category_input", "").strip()
    if new_category:
        # Get existing categories from cached board state
        existing_categories = []
        if hasattr(st.session_state, 'last_board_state'):
            try:
                import json
                board_data = st.session_state.last_board_state
                if isinstance(board_data, str):
                    board_data = json.loads(board_data)

                if isinstance(board_data, dict) and "columns" in board_data:
                    existing_categories = [col.get("title", "") for col in board_data.get("columns", [])]
            except:
                existing_categories = []

        if new_category in existing_categories:
            st.error(f"Category '{new_category}' already exists.")
        else:
            # Add category and sync state
            add_category_to_board_state(new_category)
    else:
        st.warning("Please enter a category name.")

def render_category_creator():
    """Render the interface for creating new categories"""
    st.text("If none of the categories seem to fit the class create new ones here")

    # Quick add button for instant category creation
    st.button("➕ Quick Add Category", key="quick_add_category_button", type="secondary", on_click=add_quick_category)
    

    # Optional advanced: custom named categories
    with st.container(horizontal=True):
        new_category = st.text_input(
            "Create custom category",
            key="new_category_input",
            placeholder="Custom category name (optional)",
            label_visibility="collapsed",
        )
        st.button("Add Custom", key="add_category_button", on_click=add_custom_category)
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

    # Generate unique key for the kanban board - hash of category names only


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
            key="kanban_board_component", #TEMPORARY SOLUTION
            # if on hybrid or open allow new categories by setting to true
            allow_new_categories= survey_config.get("allow_custom_categories", "Closed") in ["Open", "Hybrid"],
            rename_categories='new_only',
            debug_font=True
        )

        # Cache the actual board state after rendering and update sorted_cards
        if board_state:
            try:
                import json
                if isinstance(board_state, str):
                    board_data = json.loads(board_state)
                else:
                    board_data = board_state

                if isinstance(board_data, dict) and "columns" in board_data:
                    # Update the cached board state
                    st.session_state.last_board_state = board_data
                    # Sync board state with sorted_cards
                    sync_board_state()
                    
            except (json.JSONDecodeError, ValueError, AttributeError, TypeError) as e:
                st.error(f"Error processing board state: {str(e)}")

    return board_state


def set_completion_state(state: str, message: str):
    """Callback to set completion state"""
    st.session_state.completion_state = state
    st.session_state.completion_message = message

def reset_completion_state():
    """Reset completion state"""
    st.session_state.completion_state = None
    st.session_state.completion_message = None
    st.session_state.card_sorting_reset = True
    st.session_state.sorted_cards = None

def reset_card_sorting():
    """Callback function to reset card sorting"""
    reset_completion_state()

def handle_completion():
    """Handle the completion of card sorting"""
    container = st.container(horizontal=True, gap="medium", horizontal_alignment="right")

    container.button("Reset", type="secondary", on_click=reset_card_sorting)
    if container.button("Complete", type="primary"):
        # Check if all cards are categorized
        if st.session_state.sorted_cards.get("Uncategorized"):
            set_completion_state("error_incomplete", "Please categorize all cards before completing.")
        else:
            # All cards categorized, set processing state
            st.session_state.completion_state = "processing"
            st.rerun()
def get_uxvault_survey():
    # ask people about this page current layout instead
    """Returns the UX Vault card sorting survey configuration"""
    return {
        "id": "c8300805-5caf-49e5-912a-279c41ae9c1a",  # UX Vault survey UUID
        "title": "UX Vault Card Sorting Survey",
        "description": "Help us improve the UX Vault with a meta card sorting, categorize if the current features make sense in their category!",
        "cards": [
            "Home",
            "About us",
            "Dashboard",
            "Create Card sorting",
            "Solve Card Sorting",
            "Log In/ Sign Up",

        ],
        "use_named_categories": True,
        "categories": [
            "User",
            "Tools",
            "Who we are",
        ],
        "allow_custom_categories": "Hybrid"
    }
def get_example_survey():
    # ask people about this page current layout instead
    """Returns an example card sorting survey configuration"""
    return {
        "id": "32559d29-4118-4b52-b3e0-1b27beaf95dd",  # Test survey UUID
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
        "allow_custom_categories": "Open"
    }

def main():
    # Initialize base session state
    initialize_session_state()
    
    # Handle no active survey case
    if not st.session_state.testing_survey:
        with st.container():
            st.warning("No survey configuration found. Please create a survey first, or test our built-in examples.")
            
            with st.container(horizontal=True, gap="medium",horizontal_alignment='distribute',vertical_alignment='center'):

                card_sorting_example = st.pills("Select a card sorting example", options=["UX vault survey", "Banking app survey"],help="Choose between the built-in UX Vault survey or an example banking app survey to practice card sorting.")

                if card_sorting_example == "UX vault survey":
                    st.session_state.testing_survey = get_uxvault_survey()
                    st.rerun()
                elif card_sorting_example == "Banking app survey":
                    st.session_state.testing_survey = get_example_survey()
                    st.rerun()
                
                if st.button("Back to Survey Creation",type='primary'):
                    st.switch_page("uxvault/create_card_sorting.py")
                
        st.stop()
    
    # Initialize card sorting if needed
    survey_config = st.session_state.testing_survey
    initialize_card_sorting(survey_config)
    
    board_layout = render_header(survey_config)



    render_kanban_interface(survey_config, board_layout)
    
    # Handle completion based on session state
    if st.session_state.completion_state == "processing":
        results = {
            "survey_config": survey_config,
            "sorted_cards": st.session_state.sorted_cards,
            "completed_at": str(datetime.now())
        }
        
        survey_id = survey_config.get("id") # Get survey ID from config
        if not survey_id:
            # Set completion message for unregistered surveys
            set_completion_state("completed_no_server", "Survey completed but not submitted to servers - this is probably a test survey that isn't registered yet.")
        else:
            try:
                supabase_client.submit_survey_response(survey_id, results)
                set_completion_state("completed_success", "Your response has been stored!")
            except Exception as e:
                set_completion_state("completed_error", f"You completed the card sorting but we couldn't store the results on servers: {e}")
    
    # Display persistent completion message if state is set
    if st.session_state.completion_state and st.session_state.completion_state != "processing":
        if st.session_state.completion_state.startswith("error"):
            # Display error messages as warnings
            st.warning(st.session_state.completion_message)
        elif st.session_state.completion_state.startswith("completed"):
            # Display success/info messages as info
            st.info(st.session_state.completion_message)
        

    handle_completion()

if __name__ == "__main__":
    main()
