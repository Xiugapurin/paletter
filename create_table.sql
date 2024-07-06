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
	summary TEXT NOT NULL,
	summary_embedding vector(1536)
);

CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES "users" (user_id) ON DELETE CASCADE NOT NULL,
    sender VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    emotion VARCHAR(20) DEFAULT 'None';
    send_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE colors (
    color_id SERIAL PRIMARY KEY,
    diary_id INTEGER REFERENCES diaries(diary_id) ON DELETE CASCADE,
    user_id VARCHAR(50) NOT NULL,
    color VARCHAR(50) NOT NULL,
    content TEXT NOT NULL
);