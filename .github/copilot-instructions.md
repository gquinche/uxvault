# UX Vault AI Development Guide

## Project Overview
UX Vault is a Streamlit-based application for conducting card sorting surveys. This is a rewrite of an [original implementation](https://github.com/cronozul/p_cards) focused on maintainability and extensibility.

## Core Architecture

### Key Components
- `uxvault/landing.py` - Application entry point and navigation
- `uxvault/create_card_sorting.py` - Survey creation interface
- `uxvault/solve_card_sorting.py` - Card sorting implementation
- `static/` - Static assets (fonts, images)
- `streamlit_kanban_os` - Custom Streamlit component for drag-drop (in development)

### State Management
- Use `st.session_state` for all persistent data
- Survey configurations stored in `st.session_state["testing_survey"]`
- Card sorting state in `st.session_state.sorted_cards`

### Component Patterns
```python
# Container-based layout with native Streamlit components
with st.container(horizontal=True, gap="medium"):
    # Component content here
```

### Function Structure
```python
def render_component(data: dict):
    """Each UI component should have a clear render function"""
    with st.container():
        # Component logic
```

## Development Workflow

### Setup
1. Project uses Poetry for dependency management
2. Dependencies defined in `pyproject.toml`
3. Custom wheel files stored in root directory

### Running
```bash
streamlit run uxvault/landing.py
```

### Component Guidelines
1. Prefer native Streamlit containers over columns
2. Use horizontal=True for flex layouts
3. Avoid custom CSS - use Streamlit's built-in styling
4. Keep UI components small and focused

### Import Patterns
- For direct execution (not as a package): `from uxvault.utils.module import function`
- Avoid relative imports (`.utils.module`) for direct script execution as they require parent package context
- When calling from outside uxvault folder, treat uxvault as importable package

### State Management Rules
1. Initialize all session state in a dedicated function
2. Use consistent key naming patterns
3. Document state dependencies in function docstrings

### Execution Model
1. Streamlit executes scripts from top to bottom on each interaction
2. Use callbacks for modifying components that appear earlier in the script:
```python
def update_above_components():
    st.session_state.some_value = new_value

st.button("Update", on_click=update_above_components)  # Correct
if st.button("Update"):  # Incorrect - changes won't affect components above
    st.session_state.some_value = new_value
```
3. Callbacks run before the script reruns, ensuring state changes are available to all components

## Key Integration Points

### Streamlit Extensions
- Custom components go in `streamlit_kanban_os` package
- Version updates require wheel file regeneration
- Integration via `pyproject.toml` dependencies

### Data Flow
1. Survey Creation → Session State → Card Sorting
2. Results stored in JSON format
3. Future: Cloud storage integration planned

## Common Operations

### Adding New Survey Types
1. Extend survey configuration in `create_card_sorting.py`
2. Update initialization in `solve_card_sorting.py`
3. Add new UI components as needed

### Debugging
- Use `st.write()` for state inspection
- Check `st.session_state` for persistence issues
- Component updates trigger automatic page reruns
