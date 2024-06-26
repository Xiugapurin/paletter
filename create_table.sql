CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    llm_preference VARCHAR(255),
    profile_picture TEXT,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE diary (
    diary_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    diary_date DATE NOT NULL,
	diary_title VARCHAR(255),
    diary_content TEXT NOT NULL,
	media JSONB,
	summary TEXT NOT NULL,
	summary_embedding vector(1536) NOT NULL
);

CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user" (user_id) ON DELETE CASCADE NOT NULL,
    sender VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    send_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);