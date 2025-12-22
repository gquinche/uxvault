-- Enable the uuid-ossp extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table for storing card sorting surveys
CREATE TABLE surveys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    config JSONB -- For survey-specific settings like categories, etc.
);

-- Table for storing survey responses
CREATE TABLE responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    survey_id UUID NOT NULL REFERENCES surveys(id) ON DELETE CASCADE,
    -- responder_id UUID, -- Optional: if responses need to be linked to specific anonymous/logged-in responders
    response_data JSONB NOT NULL, -- Containing the actual survey responses
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Row Level Security (RLS) policies

-- Surveys: Users can only access their own surveys
ALTER TABLE surveys ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow users to view their own surveys" ON surveys FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Allow users to create their own surveys" ON surveys FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Allow users to update their own surveys" ON surveys FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Allow users to delete their own surveys" ON surveys FOR DELETE USING (auth.uid() = user_id);

-- Responses: Users can only view responses for their own surveys
ALTER TABLE responses ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow users to view responses for their own surveys" ON responses FOR SELECT USING (
    EXISTS (
        SELECT 1
        FROM surveys
        WHERE surveys.id = responses.survey_id AND surveys.user_id = auth.uid()
    )
);
-- Note: For submitting responses, we might not need RLS on the 'responses' table itself if the API handles it,
-- or we can add a policy that allows any authenticated user to insert if they have a valid survey_id.
-- For now, assuming the API will handle submission and we only need RLS for retrieval.
-- If direct insertion via SQL is allowed, a policy like this might be needed:
-- CREATE POLICY "Allow anyone to submit responses to existing surveys" ON responses FOR INSERT WITH CHECK (
--     EXISTS (
--         SELECT 1
--         FROM surveys
--         WHERE surveys.id = responses.survey_id
--     )
-- );

-- Trigger to update 'updated_at' timestamp for surveys
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_surveys_updated_at
BEFORE UPDATE ON surveys
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- You would typically apply this SQL script to your Supabase project via the SQL Editor.
-- For authentication, ensure Google OAuth is enabled in Supabase Auth settings.
