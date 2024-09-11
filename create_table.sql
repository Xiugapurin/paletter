CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    llm_preference VARCHAR(255),
    profile_picture TEXT,
    membership_level VARCHAR(20) DEFAULT 'Basic',
    credit_limit INTEGER DEFAULT 0,
    has_completed_diary BOOLEAN DEFAULT FALSE,
    is_trial BOOLEAN DEFAULT TRUE,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE diaries (
    diary_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES "users" (user_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    content TEXT NOT NULL,
    media JSONB,
	status VARCHAR(20) NOT NULL,
	type VARCHAR(20) NOT NULL,
    summary VARCHAR(255),
	tag VARCHAR(50)
);

CREATE TABLE diary_chunks (
    chunk_id SERIAL PRIMARY KEY,
    diary_id INTEGER REFERENCES "diaries" (diary_id) ON DELETE CASCADE,
    user_id VARCHAR(50) NOT NULL,
    chunk_content TEXT,
    embedding vector(1536)
);

CREATE TABLE colors (
    color_id SERIAL PRIMARY KEY,
    diary_id INTEGER REFERENCES "diaries" (diary_id) ON DELETE CASCADE,
    user_id VARCHAR(50) NOT NULL,
    color VARCHAR(50) NOT NULL,
    type VARCHAR(20),
    content TEXT NOT NULL
);

CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES "users" (user_id) ON DELETE CASCADE,
    sender VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    send_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);