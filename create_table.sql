CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    llm_preference VARCHAR(255),
    profile_picture TEXT,
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
	tag VARCHAR(255),
	color VARCHAR(20) NOT NULL,
	summary TEXT NOT NULL,
	summary_embedding vector(1536)
);

CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES "users" (user_id) ON DELETE CASCADE NOT NULL,
    sender VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    send_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);