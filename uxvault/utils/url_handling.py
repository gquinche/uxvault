import streamlit as st
import json
import base64
from typing import Optional, Tuple

def encode_survey(survey_config: dict, use_base64: bool = False) -> str:
    """Encode survey configuration for URL sharing"""
    if use_base64:
        json_str = json.dumps(survey_config)
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        return f"survey_b64={encoded}"
    return f"survey={json.dumps(survey_config)}"

def decode_survey(query_params: dict) -> Tuple[Optional[dict], str]:
    """
    Decode survey configuration from URL parameters
    Returns: (survey_config, error_message)
    """
    try:
        if "survey_b64" in query_params:
            encoded_survey = query_params["survey_b64"]
            json_str = base64.b64decode(encoded_survey).decode('utf-8')
            return json.loads(json_str), ""
        elif "survey" in query_params:
            return json.loads(query_params["survey"]), ""
        return None, "No survey configuration found in URL"
    except base64.binascii.Error:
        return None, "Invalid base64 encoding"
    except json.JSONDecodeError:
        return None, "Invalid JSON format"
    except Exception as e:
        return None, f"Error decoding survey: {str(e)}"

def get_share_url(survey_config: dict, use_base64: bool = False) -> str:
    """Generate complete sharing URL for survey"""
    # Get the base URL from Streamlit context (excludes query params and anchors)
    base_url = st.context.url
    
    # Replace the current page with solve_card_sorting
    if "create_card_sorting" in base_url:
        base_url = base_url.replace("create_card_sorting", "solve_card_sorting")
    elif not base_url.endswith("solve_card_sorting"):
        base_url = f"{base_url}/solve_card_sorting"
    
    # Remove any trailing slashes
    base_url = base_url.rstrip('/')
    
    # Add query parameters
    query_param = encode_survey(survey_config, use_base64)
    return f"{base_url}?{query_param}"

def get_survey_id_from_url() -> Optional[str]:
    """
    Extracts the survey ID from the URL query parameters.
    Assumes the survey ID is part of the decoded survey configuration.
    """
    query_params = st.query_params
    survey_config, error_message = decode_survey(query_params)

    if survey_config and "id" in survey_config:
        return survey_config["id"]
    return None