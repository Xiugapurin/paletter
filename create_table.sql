CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    profile_picture TEXT,
    membership_level VARCHAR(15) DEFAULT 'Basic' NOT NULL,
    credit_limit INTEGER DEFAULT 0 NOT NULL,
    is_trial BOOLEAN DEFAULT TRUE NOT NULL,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE diaries (
    diary_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users (user_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    reply_paletter_code VARCHAR(31) DEFAULT '' NOT NULL,
	reply_content TEXT DEFAULT '' NOT NULL,
    reply_picture TEXT DEFAULT '' NOT NULL
);

CREATE TABLE diary_entries (
    diary_entry_id SERIAL PRIMARY KEY,
    diary_id INTEGER REFERENCES diaries (diary_id) ON DELETE CASCADE,
    title VARCHAR(63) DEFAULT '' NOT NULL,
    content TEXT DEFAULT '' NOT NULL,
    emotion VARCHAR(15) DEFAULT '' NOT NULL,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_edit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE paletters (
    paletter_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users (user_id) ON DELETE CASCADE,
    paletter_code VARCHAR(31) NOT NULL,
    intimacy_level INTEGER CHECK (intimacy_level BETWEEN 0 AND 100) DEFAULT 0 NOT NULL,
    vitality_value INTEGER CHECK (vitality_value BETWEEN 0 AND 500) DEFAULT 500 NOT NULL,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_chat_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users (user_id) ON DELETE CASCADE,
    paletter_id INTEGER REFERENCES paletters (paletter_id) ON DELETE CASCADE,
    sender VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    send_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE knowledge (
    knowledge_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users (user_id) ON DELETE CASCADE,
    paletter_id INTEGER REFERENCES paletters (paletter_id) ON DELETE CASCADE,
    source VARCHAR(15) NOT NULL,
    source_id INTEGER DEFAULT -1 NOT NULL,
    date DATE NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    activate_count INTEGER DEFAULT 0 NOT NULL,
    is_activate BOOLEAN DEFAULT TRUE NOT NULL
);