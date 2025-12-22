import streamlit as st
from st_supabase_connection import SupabaseConnection, execute_query


def _get_anon_client(secrets: dict = None):
    """
    Internal helper to get a Supabase client.
    
    Returns the cached Streamlit connection. The client uses its internal state
    to store the session JWT, which is automatically included in all requests
    via the Authorization header.
    
    Call get_authenticated_client() first to restore the session to the client's
    internal state before making authenticated requests.
    """
    try:
        cfg = secrets or st.secrets.get("connections", {}).get("supabase", {})
        client = st.connection(
            name="supabase",
            type=SupabaseConnection,
            ttl=None,  # Cache indefinitely; override when you need fresher data
            url=cfg.get("SUPABASE_URL"),
            key=cfg.get("SUPABASE_KEY"),
        )
        return client
    except Exception as e:
        st.error(f"There was an error connecting to our databases: {e}")
        return None
@st.cache_data(ttl=3600,max_entries=1000) # won't hash or cache _client
def sign_up(email: str, password: str, _client: SupabaseConnection = None, is_hacky_google_oauth: bool = False):
    """
    Signs up a new user with the given email and password.
    
    If no client is provided, uses an anonymous Supabase client.
    
    Args:
        email (str): User's email address.
        password (str): User's password.
        client (SupabaseConnection, optional): Supabase client to use. Defaults to None.
        is_hacky_google_oauth (bool, optional): Whether to use hacky Google OAuth signup. Defaults to False.
    
    Returns:
        dict: Response from the sign-up attempt.
    """
    try:
        # TODO check weird bug where we aren't sending the correct email
        response = _client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"hacky_google_oauth": is_hacky_google_oauth}
        })
        return response
    except Exception as e:
        # Try to use the specific exception when available
        AuthApiError = None
        try:
            # Try importing from the supabase package where the error usually lives.
            # Adjust this import if your package exposes it elsewhere.
            from supabase import AuthApiError
        except Exception:
            try:
                # Some versions expose it under a different path:
                from supabase.lib.client import AuthApiError
            except Exception:
                AuthApiError = None

        # If we have the class, use isinstance — safer than string matching
        if AuthApiError and isinstance(e, AuthApiError) and 'User already registered' in str(e):
            #st.info("User is already registered, proceeding to sign in.")
            # this gets catched and shown which is confusing

            return {'user': {'email': email}}

        # Fallback: inspect the message string (less robust but works across versions)
        if 'User already registered' in str(e) or getattr(e, 'message', '') == 'User already registered':
            #st.info("User is already registered, proceeding to sign in.")
            # this gets catched and shown which is confusing
            return {'user': {'email': email}}

        # Otherwise bubble up a useful error
        st.info(f"Error signing up: {e} we tried searching for your user email {email} but got an error")
        # TODO fix this by updating to new supabase message which seems to be error finding user 
        # even if it exists
        return None

    
@st.cache_data(ttl=3600,max_entries=1000)
def sign_in(email: str, password: str, _client: SupabaseConnection = None):
    """
    Signs in a user with the given email and password.
    
    If no client is provided, uses an anonymous Supabase client.
    
    Args:
        email (str): User's email address.
        password (str): User's password.
        client (SupabaseConnection, optional): Supabase client to use. Defaults to None.
    
    Returns:
        dict: Response from the sign-in attempt.
    """
    try:
        response = _client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response == 'User is already registered':
            st.info("User is already registered, proceeding to sign in.")
        return response
    except Exception as e:
        st.error(f"Error signing in: {e}")
        return None
    
def get_authenticated_client(user = None, secrets: dict = None):
    """
    Returns an authenticated Supabase client.
    
    If a session already exists in st.session_state, restores it to the client's
    internal state and returns the client. Otherwise, attempts Google OAuth login.
    
    The returned client will include the session JWT in all requests automatically.
    
    Returns:
        SupabaseConnection or None: Authenticated client, or None if authentication fails.
    """
        
    if not user or not getattr(user, 'is_logged_in', False):
        st.write("You tried to access a feature only for logged in users. Please log in first.")
        st.warning("If you think this is an error, please contact us through github.")
        return None
    # cfg = secrets or st.secrets.get("connections", {}).get("supabase", {})
    # st.write(cfg.get("SUPABASE_URL"))
    # st.write(st.secrets)
    # st.write(secrets)
    client = st.connection(
        name=getattr(user, 'email', 'user') + "_supabase_connection",
        type=SupabaseConnection,
        ttl=3600,
        url=secrets.get("SUPABASE_URL"),
        key=secrets.get("SUPABASE_KEY"),
    )

    email = getattr(user, 'email', None)
    password = getattr(user, 'sub', None)

    if client is None:
        st.write("Unable to connect to our servers, please try again later.")
        return None

    # Use session_state dict passed in to avoid implicit global mutation
    sign_up_response = sign_up(email, password, client, is_hacky_google_oauth=True)
    if sign_up_response is None:
        st.write("Error checking if your account exists. Please try again.")
        return None
    sign_in_response = sign_in(email, password, client)
    if sign_in_response is None or getattr(sign_in_response, 'error', None):
        st.write("Error signing in. Please try again.")
        return None

    return client

# Sign out is not implemented because singin out would disconnect users from other web explorers, instead the ttl 
# ensures we don't collect too many open connections ensure there are not collision in user names
def sign_out():
    pass
 
# --- Survey Management Functions ---

def create_survey(title: str, description: str = "", config: dict = None, client: SupabaseConnection = None, user_id: str = None, session_state: dict = None):
    """
    Creates a new card sorting survey.
    Requires user to be authenticated.
    """

    session_state = session_state if session_state is not None else getattr(st, 'session_state', {})
    if client is None:
        client = get_authenticated_client(session_state=session_state)
    if client is None:
        raise Exception("Unable to get authenticated Supabase client.")

    resolved_user_id = user_id if user_id is not None else session_state.get('user_id')
    if not resolved_user_id:
        try:
            resolved_user_id = client.auth.get_user().user.id
        except Exception:
            resolved_user_id = None

    survey_data = {
        "title": title,
        "description": description,
        "user_id": resolved_user_id,
        "config": config if config is not None else {}
    }
    try:
        # Use execute_query for database operations
        response = execute_query(
            client.table("surveys").insert(survey_data),
            ttl=0 # No caching for inserts
        )
        if response and hasattr(response, 'data') and response.data:
            created_survey = response.data[0]
            st.write(f"Survey '{title}' created successfully")
            return created_survey
        else:
            error_msg = getattr(response, 'error', "Unknown error") if response else "No response data"
            st.write(f"Failed to create survey: {error_msg}")
            raise Exception(f"Failed to create survey: {error_msg}")
    except Exception as e:
        st.write(f"Error creating survey: {e}")
        raise

def get_user_surveys(client: SupabaseConnection = None, user_email: str = None):
    """
    Retrieves all surveys belonging to the authenticated user.
    """
    try:
        # Use execute_query for database operations
        if client.auth.get_user is not None and client.auth.get_user().user is None:
            st.write("You can't access surveys without being logged in.")
            return []
        response = execute_query(
            client.table("surveys").select("*").order("created_at", desc=True),
            ttl="5m" # Cache surveys for 5 minutes
        )
        retrieved_count = len(response.data)
        st.write(f"Retrieved {retrieved_count} surveys..")
        return response.data

    except Exception as e:
        st.write(f"Error retrieving surveys: {e}")
        raise

def get_user_surveys_responses(client: SupabaseConnection = None):
    """
    Retrieves all surveys and their responses belonging to the authenticated user.
    """

    if client is None or hasattr(client.auth.get_user(), 'user') and client.auth.get_user().user is None:
        st.write("You can't access surveys with responses without being logged in.")
        return []
    try:
        # Use execute_query for database operations
        response = execute_query(
            client.table("responses").select("*") #.order("submitted_at", desc=True),
            ,ttl="1m" # Cache surveys for 1 minute
        )
        
        if response and hasattr(response, 'data') and response.data is not None:
            return response
        else:
            error_msg = getattr(response, 'error', "No data or unknown error") if response else "No response data"
            st.write(f"No surveys found or error retrieving surveys with responses: {error_msg}")
            return []
    except Exception as e:
        st.write(f"Error retrieving surveys with responses: {e}")
        raise

def submit_survey_response(survey_id: str, response_data: dict, client: SupabaseConnection = None):
    """
    Submits a response to a specific survey.
    Uses the Supabase client - assumes responses are public/unauthenticated.
    """
    client = client or _get_anon_client()
    if client is None:
        st.write("Supabase client not initialized, cannot submit response.")
        raise Exception("Supabase client not initialized. Please check your Supabase connection.")

    # Note: RLS on 'responses' table is set to allow anyone to view responses for *their own* surveys.
    # For submission, we might not need user authentication here if the survey is public,
    # or if we want to allow anonymous responses.
    # If only authenticated users can submit, we'd use get_current_user_id() and potentially
    # add responder_id to the response_entry.
    # For now, assuming submission is open if survey_id is valid.

    response_entry = {
        "survey_id": survey_id,
        "response_data": response_data,
        # "responder_id": user_id if user_id else None # Uncomment if you want to track responders
    }
    try:
        response = execute_query(
            client.table("responses").insert(response_entry),
            ttl=0 # No caching for inserts
        )
        if response and hasattr(response, 'data') and response.data:
            return response.data[0]
        else:
            error_msg = getattr(response, 'error', "Unknown error") if response else "No response data"
            st.write(f"Failed to submit survey response: {error_msg}")
            raise Exception(f"Failed to submit response: {error_msg}")
    except Exception as e:
        st.write(f"Error submitting response: {e}")
        raise

