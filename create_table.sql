CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    llm_preference VARCHAR(255),
    profile_picture TEXT,
    membership_level VARCHAR(15) DEFAULT "Basic" NOT NULL,
    credit_limit INTEGER DEFAULT 0 NOT NULL,
    has_completed_diary BOOLEAN DEFAULT FALSE NOT NULL,
    is_trial BOOLEAN DEFAULT TRUE NOT NULL,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login TIMESTAMP
);

CREATE TABLE diaries (
    diary_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES "users" (user_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    content TEXT DEFAULT '' NOT NULL,
    media JSONB,
	status VARCHAR(15) NOT NULL,
	type VARCHAR(15) DEFAULT '' NOT NULL,
    summary VARCHAR(255) DEFAULT '',
	tag VARCHAR(63) DEFAULT ''
);

CREATE TABLE diary_messages (
    diary_message_id SERIAL PRIMARY KEY,
    diary_id INTEGER REFERENCES "diaries" (diary_id) ON DELETE CASCADE,
    user_id VARCHAR(50) NOT NULL,
    sender VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    send_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE colors (
    color_id SERIAL PRIMARY KEY,
    diary_id INTEGER REFERENCES "diaries" (diary_id) ON DELETE CASCADE,
    user_id VARCHAR(50) NOT NULL,
    color VARCHAR(50) NOT NULL,
    type VARCHAR(20),
    content TEXT DEFAULT '' NOT NULL
);

CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES "users" (user_id) ON DELETE CASCADE,
    sender VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    send_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE knowledge (
    knowledge_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES "users" (user_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    owner VARCHAR(15) NOT NULL,
    content TEXT NOT NULL,
    is_activate BOOLEAN DEFAULT TRUE NOT NULL,
    embedding vector(1536)
)