# Backend Requirements Document for Streamlit Card Sorting App

## 1. Introduction
This document outlines the requirements for the backend solution that will support the Streamlit card sorting application. The backend will handle user authentication, manage survey data, and retrieve survey responses.

## 2. Technology Stack
*   **Backend Framework:** Python (compatible with Streamlit)
*   **Database:** Supabase (PostgreSQL)
*   **Authentication:** Google OAuth 2.0 via Supabase Auth

## 3. User Authentication
*   **Requirement:** Users must be able to log in using their Google accounts.
*   **Mechanism:** Integrate Google OAuth 2.0 with Supabase Auth.
*   **Outcome:** Upon successful login, Supabase Auth will provide user credentials (e.g., JWT) that grant access to personalized data.
*   **Data Storage:** User information (e.g., user ID, email) will be stored securely in Supabase.

## 4. Data Management
### 4.1. Card Sorting Surveys
*   **Requirement:** Users must be able to access all their previously created card sorting surveys.
*   **Data Model:**
    *   `surveys` table:
        *   `id` (UUID, primary key)
        *   `user_id` (UUID, foreign key to Supabase auth users)
        *   `title` (VARCHAR)
        *   `description` (TEXT)
        *   `created_at` (TIMESTAMP)
        *   `updated_at` (TIMESTAMP)
        *   `config` (JSONB, for survey-specific settings like card categories, etc.)
*   **Functionality:**
    *   Create new surveys.
    *   Retrieve a list of all surveys belonging to the authenticated user.
    *   View details of a specific survey.
    *   (Optional: Edit/Delete surveys)

### 4.2. Survey Responses
*   **Requirement:** Users must be able to view all responses submitted to their surveys.
*   **Data Model:**
    *   `responses` table:
        *   `id` (UUID, primary key)
        *   `survey_id` (UUID, foreign key to `surveys` table)
        *   `responder_id` (UUID, optional, if responses need to be linked to specific anonymous/logged-in responders)
        *   `response_data` (JSONB, containing the actual survey responses, e.g., card placements, ratings)
        *   `submitted_at` (TIMESTAMP)
*   **Functionality:**
    *   Retrieve all responses for a given survey.
    *   (Optional: Filter/aggregate responses)

## 5. API Endpoints
The backend will expose RESTful API endpoints for the Streamlit frontend to interact with. These endpoints will be secured and require authentication.

### 5.1. Authentication Endpoints
*   `POST /auth/google`: Initiates Google OAuth flow.
*   `GET /auth/callback`: Handles the OAuth callback and returns user session/token.

### 5.2. Survey Endpoints
*   `POST /surveys`: Create a new survey.
    *   Request Body: Survey details (title, description, config).
    *   Response: Newly created survey object.
*   `GET /surveys`: Get all surveys for the authenticated user.
    *   Response: List of survey objects.
*   `GET /surveys/{survey_id}`: Get details of a specific survey.
    *   Response: Survey object.

### 5.3. Response Endpoints
*   `POST /surveys/{survey_id}/responses`: Submit a response to a survey.
    *   Request Body: Response data.
    *   Response: Confirmation of submission.
*   `GET /surveys/{survey_id}/responses`: Get all responses for a specific survey.
    *   Response: List of response objects.

## 6. Supabase Integration
*   **Authentication:** Configure Supabase Auth with Google OAuth provider.
*   **Database:**
    *   Create `surveys` and `responses` tables with appropriate schemas and RLS (Row Level Security) policies to ensure users can only access their own data.
    *   Set up foreign key constraints.
*   **Client Library:** Use the Supabase Python client library to interact with the database and authentication.

## 7. Security
*   All API endpoints must be protected by authentication.
*   Implement Row Level Security (RLS) in Supabase to ensure data privacy and prevent unauthorized access to surveys and responses.
*   Sanitize all user inputs to prevent SQL injection and other vulnerabilities.

## 8. Future Considerations (Optional)
*   Survey analytics and reporting.
*   User management features (e.g., inviting collaborators).
*   Real-time updates for responses.
