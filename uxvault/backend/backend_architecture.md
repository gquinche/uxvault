# Backend Architecture for Streamlit Card Sorting App

This document describes the overall architecture of the backend solution for the Streamlit card sorting application. It details how different components interact to provide authentication, data management, and API access.

## 1. Overview

The backend architecture is designed to be lightweight and leverage Supabase for database and authentication services. The Streamlit application will interact with Supabase directly using the Supabase Python client library.

## 2. Core Components

*   **Streamlit Frontend:** The user interface built with Streamlit. It handles user interactions, displays data, and makes requests to the backend services.
*   **Supabase:** A Backend-as-a-Service (BaaS) platform that provides:
    *   **Supabase Auth:** Handles user authentication, including Google OAuth 2.0.
    *   **Supabase Database:** A PostgreSQL database storing survey and response data. It enforces data integrity and security through Row Level Security (RLS).
    *   **Supabase Realtime (Optional):** For real-time updates if needed in the future.
*   **Supabase Python Client Library:** A Python library used by the Streamlit application to communicate with Supabase Auth and the Supabase Database.

## 3. Data Flow

1.  **User Authentication:**
    *   The user initiates login via Google OAuth from the Streamlit frontend.
    *   The Streamlit app uses the Supabase Python client to interact with Supabase Auth for the OAuth flow.
    *   Supabase Auth handles the redirection to Google, user verification, and returns a JWT (JSON Web Token) to the client.
    *   The Supabase client library manages the user session using this JWT.

2.  **Survey Management:**
    *   When a user wants to create, view, or manage their surveys, the Streamlit frontend calls functions from `supabase_client.py`.
    *   These functions use the Supabase Python client to make authenticated requests to the Supabase Database (e.g., `POST /surveys`, `GET /surveys`).
    *   Supabase Auth ensures that requests are authenticated, and RLS policies on the `surveys` table ensure users can only access their own data.

3.  **Survey Response Management:**
    *   When a user submits a response to a survey, the Streamlit frontend calls `submit_survey_response` from `supabase_client.py`. This function inserts data into the `responses` table.
    *   When a user views responses for their surveys, the Streamlit frontend calls `get_survey_responses` from `supabase_client.py`.
    *   Supabase Auth and RLS policies on the `responses` table ensure that only the owner of the survey can view its associated responses.

## 4. Key Files and Technologies

*   **`backend_requirements.md`:** High-level requirements for the backend.
*   **`supabase/schema.sql`:** SQL script defining the database schema (`surveys`, `responses` tables) and RLS policies in Supabase.
*   **`api_endpoints.md`:** Documentation of conceptual API endpoints, primarily leveraging Supabase's auto-generated REST API.
*   **`supabase_client.py`:** Python module containing functions to interact with Supabase Auth and Database. This acts as the primary backend logic interface for the Streamlit app.
*   **Streamlit Application (`.py` files):** The frontend application that orchestrates user interactions and calls functions in `supabase_client.py`.
*   **Supabase Project:** The cloud-hosted Supabase instance managing authentication and the PostgreSQL database.

## 5. Security Considerations

*   **Authentication:** Handled by Supabase Auth with Google OAuth.
*   **Authorization:** Enforced by Supabase Row Level Security (RLS) policies on database tables, ensuring users can only access their own data.
*   **Data Integrity:** Ensured by PostgreSQL constraints and Supabase's data validation.

## 6. Future Enhancements

*   Implementing more sophisticated analytics on survey responses.
*   Adding features for survey collaboration or sharing.
*   Potentially introducing a dedicated backend API layer (e.g., FastAPI) if complexity grows beyond direct Supabase interaction.
