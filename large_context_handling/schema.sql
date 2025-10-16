-- Context Decomposition Strategy - Database Schema
-- SQLite 3.x

-- Labels: Store labeled context chunks
CREATE TABLE IF NOT EXISTS labels (
    id TEXT PRIMARY KEY,
    clause_summary TEXT NOT NULL,
    data TEXT NOT NULL,              -- JSON serialized data
    size_kb REAL,
    created_turn INTEGER,
    last_accessed_turn INTEGER,
    access_count INTEGER DEFAULT 0,
    parent_id TEXT,                  -- For hierarchical labels (future)
    metadata TEXT,                   -- JSON for extensibility
    FOREIGN KEY (parent_id) REFERENCES labels(id)
);

-- Conversation history: Track all turns
CREATE TABLE IF NOT EXISTS conversation_history (
    turn_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    token_count INTEGER,
    decomposed BOOLEAN DEFAULT FALSE
);

-- Decompositions: Track when questions were decomposed
CREATE TABLE IF NOT EXISTS decompositions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    turn_id INTEGER,
    original_question TEXT NOT NULL,
    num_sub_questions INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (turn_id) REFERENCES conversation_history(turn_id)
);

-- Sub-questions: Individual sub-question details
CREATE TABLE IF NOT EXISTS sub_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decomposition_id INTEGER,
    sub_q_id TEXT,                   -- Q1, Q2, Q3, etc.
    question_text TEXT NOT NULL,
    answer_text TEXT,
    labels_used TEXT,                -- JSON array: ["L1", "L2"]
    depends_on TEXT,                 -- JSON array: ["Q1", "Q2"]
    execution_wave INTEGER,
    FOREIGN KEY (decomposition_id) REFERENCES decompositions(id)
);

-- Label access log: Track access patterns for evolution triggers
CREATE TABLE IF NOT EXISTS label_access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label_id TEXT,
    turn_id INTEGER,
    accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (label_id) REFERENCES labels(id),
    FOREIGN KEY (turn_id) REFERENCES conversation_history(turn_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_labels_size ON labels(size_kb);
CREATE INDEX IF NOT EXISTS idx_labels_access ON labels(last_accessed_turn);
CREATE INDEX IF NOT EXISTS idx_labels_parent ON labels(parent_id);
CREATE INDEX IF NOT EXISTS idx_access_log_label ON label_access_log(label_id);
CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON conversation_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_decompositions_turn ON decompositions(turn_id);
