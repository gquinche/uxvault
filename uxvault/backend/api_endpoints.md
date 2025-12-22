# API Endpoints for Streamlit Card Sorting Backend

This document outlines the API endpoints that will be exposed by the backend service to support the Streamlit card sorting application. These endpoints are designed to be consumed by the frontend and are secured via Supabase authentication.

## Base URL

The base URL for the API will depend on your Supabase project setup. It typically follows the pattern: `https://<your-project-ref>.supabase.co/rest/v1/` for direct database access, or a custom backend server if one is implemented. For this document, we'll assume direct Supabase REST API interaction where applicable, or conceptual endpoints if a separate backend service is implied.

## Authentication Endpoints

These endpoints are conceptual and would typically be handled by Supabase's client libraries or a dedicated auth server.

### 1. User Sign-up/Login (Google OAuth)

*   **Endpoint:** (Handled by Supabase Auth client library)
*   **Method:** N/A (Client-side initiated)
*   **Description:** Initiates the Google OAuth flow. The user is redirected to Google to authenticate, and upon successful authentication, is redirected back to the application with a session token.
*   **Supabase Integration:** Configure Google as an OAuth provider in Supabase Auth settings. Use Supabase client libraries (e.g., `supabase-python`) to manage the sign-in process.

### 2. Get Current User Session

*   **Endpoint:** (Handled by Supabase Auth client library)
*   **Method:** N/A
*   **Description:** Retrieves the current authenticated user's session information. This is typically done by checking for a valid JWT token.

## Survey Management Endpoints

These endpoints interact with the `surveys` table in Supabase. All endpoints require an authenticated user.

### 1. Create a New Survey

*   **Endpoint:** `/surveys`
*   **Method:** `POST`
*   **Description:** Creates a new card sorting survey for the authenticated user.
*   **Request Body:**
    ```json
    {
        "title": "My New Survey",
        "description": "A survey about user preferences.",
        "config": {
            "categories": ["Category A", "Category B"],
            "cards": ["Card 1", "Card 2"]
        }
    }
    ```
*   **Response (Success - 201 Created):**
    ```json
    {
        "id": "uuid-of-new-survey",
        "user_id": "current-user-id",
        "title": "My New Survey",
        "description": "A survey about user preferences.",
        "created_at": "2023-11-07T10:00:00Z",
        "updated_at": "2023-11-07T10:00:00Z",
        "config": {
            "categories": ["Category A", "Category B"],
            "cards": ["Card 1", "Card 2"]
        }
    }
    ```
*   **Response (Error - e.g., 401 Unauthorized, 400 Bad Request):** Standard error response.

### 2. Get All User Surveys

*   **Endpoint:** `/surveys`
*   **Method:** `GET`
*   **Description:** Retrieves a list of all surveys created by the authenticated user.
*   **Query Parameters:**
    *   `select`: Comma-separated list of columns to retrieve (e.g., `id,title,created_at`). Defaults to `*`.
    *   `order`: Column to order by (e.g., `created_at.desc`).
*   **Response (Success - 200 OK):**
    ```json
    [
        {
            "id": "uuid-of-survey-1",
            "title": "Survey One",
            "description": "Description for survey one.",
            "created_at": "2023-11-06T09:00:00Z",
            "updated_at": "2023-11-06T09:00:00Z",
            "config": { ... }
        },
        {
            "id": "uuid-of-survey-2",
            "title": "Survey Two",
            "description": "Description for survey two.",
            "created_at": "2023-11-05T11:00:00Z",
            "updated_at": "2023-11-05T11:00:00Z",
            "config": { ... }
        }
    ]
    ```
*   **Response (Error - e.g., 401 Unauthorized):** Standard error response.

### 3. Get Specific Survey Details

*   **Endpoint:** `/surveys/{survey_id}`
*   **Method:** `GET`
*   **Description:** Retrieves the details of a specific survey by its ID. The user must own this survey.
*   **URL Parameters:**
    *   `survey_id`: The UUID of the survey to retrieve.
*   **Response (Success - 200 OK):**
    ```json
    {
        "id": "uuid-of-survey-1",
        "title": "Survey One",
        "description": "Description for survey one.",
        "created_at": "2023-11-06T09:00:00Z",
        "updated_at": "2023-11-06T09:00:00Z",
        "config": { ... }
    }
    ```
*   **Response (Error - e.g., 401 Unauthorized, 404 Not Found):** Standard error response.

## Survey Response Endpoints

These endpoints interact with the `responses` table in Supabase.

### 1. Submit a Response to a Survey

*   **Endpoint:** `/surveys/{survey_id}/responses`
*   **Method:** `POST`
*   **Description:** Submits a new response for a specified survey.
*   **URL Parameters:**
    *   `survey_id`: The UUID of the survey to submit a response to.
*   **Request Body:**
    ```json
    {
        "response_data": {
            "card_placements": {
                "Card 1": "Category A",
                "Card 2": "Category B"
            },
            "rating": 5
        }
        // Optional: "responder_id": "anonymous-id-or-user-id"
    }
    ```
*   **Response (Success - 201 Created):**
    ```json
    {
        "id": "uuid-of-new-response",
        "survey_id": "uuid-of-survey-1",
        "response_data": { ... },
        "submitted_at": "2023-11-07T11:00:00Z"
    }
    ```
*   **Response (Error - e.g., 400 Bad Request, 404 Survey Not Found):** Standard error response.

### 2. Get All Responses for a Survey

*   **Endpoint:** `/surveys/{survey_id}/responses`
*   **Method:** `GET`
*   **Description:** Retrieves all responses submitted for a specific survey. The authenticated user must own the survey.
*   **URL Parameters:**
    *   `survey_id`: The UUID of the survey whose responses are to be retrieved.
*   **Query Parameters:**
    *   `select`: Comma-separated list of columns to retrieve (e.g., `id,response_data,submitted_at`). Defaults to `*`.
    *   `order`: Column to order by (e.g., `submitted_at.asc`).
*   **Response (Success - 200 OK):**
    ```json
    [
        {
            "id": "uuid-of-response-1",
            "survey_id": "uuid-of-survey-1",
            "response_data": { ... },
            "submitted_at": "2023-11-07T11:00:00Z"
        },
        {
            "id": "uuid-of-response-2",
            "survey_id": "uuid-of-survey-1",
            "response_data": { ... },
            "submitted_at": "2023-11-07T11:05:00Z"
        }
    ]
    ```
*   **Response (Error - e.g., 401 Unauthorized, 404 Survey Not Found):** Standard error response.

## Notes on Supabase Integration

*   **Direct API Access:** Supabase automatically generates RESTful APIs for your tables. You can leverage these directly.
*   **RLS:** Row Level Security policies defined in `supabase/schema.sql` are crucial for ensuring data privacy and security. They enforce that users can only access/modify their own data.
*   **Client Libraries:** Use the official Supabase client libraries (e.g., `supabase-python`) in your Streamlit app to interact with Supabase Auth and the database. These libraries abstract away much of the direct API interaction and handle JWT management.
