-- Riverse SQLite Schema

-- User conversations
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    processed INTEGER DEFAULT 0
);

-- User profile facts (core table)
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    category TEXT NOT NULL,
    subject TEXT NOT NULL,
    value TEXT NOT NULL,
    layer TEXT DEFAULT 'suspected',
    source_type TEXT DEFAULT 'stated',
    start_time TEXT DEFAULT (datetime('now')),
    end_time TEXT,
    decay_days INTEGER DEFAULT 90,
    expires_at TEXT,
    evidence TEXT DEFAULT '[]',
    mention_count INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    confirmed_at TEXT,
    superseded_by INTEGER,
    supersedes INTEGER,
    rejected INTEGER DEFAULT 0
);

-- Observations
CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    observation_type TEXT NOT NULL,
    content TEXT NOT NULL,
    subject TEXT,
    context TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    rejected INTEGER DEFAULT 0,
    classification TEXT
);

-- Events
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    category TEXT NOT NULL,
    summary TEXT NOT NULL,
    importance REAL DEFAULT 0.5,
    session_id TEXT,
    decay_days INTEGER,
    expires_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Relationships
CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    name TEXT,
    relation TEXT NOT NULL,
    details TEXT DEFAULT '{}',
    mention_count INTEGER DEFAULT 1,
    status TEXT DEFAULT 'active',
    first_mentioned_at TEXT DEFAULT (datetime('now')),
    last_mentioned_at TEXT DEFAULT (datetime('now'))
);

-- User model (personality dimensions)
CREATE TABLE IF NOT EXISTS user_model (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    dimension TEXT NOT NULL,
    assessment TEXT NOT NULL,
    evidence_summary TEXT,
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, dimension)
);

-- Trajectory summary
CREATE TABLE IF NOT EXISTS trajectory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    life_phase TEXT,
    phase_characteristics TEXT,
    trajectory_direction TEXT,
    stability_assessment TEXT,
    key_anchors TEXT DEFAULT '[]',
    volatile_areas TEXT DEFAULT '[]',
    recent_momentum TEXT,
    full_summary TEXT,
    session_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Strategies
CREATE TABLE IF NOT EXISTS strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    category TEXT NOT NULL,
    subject TEXT NOT NULL,
    strategy_type TEXT NOT NULL,
    description TEXT NOT NULL,
    trigger_condition TEXT,
    approach TEXT,
    priority REAL DEFAULT 0.5,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT
);

-- Session tags
CREATE TABLE IF NOT EXISTS session_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    summary TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Session summaries
CREATE TABLE IF NOT EXISTS session_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL UNIQUE,
    intent_summary TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Memory snapshot (pre-compiled profile for fast access)
CREATE TABLE IF NOT EXISTS memory_snapshot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    snapshot_text TEXT NOT NULL,
    profile_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_conversations_user_processed ON conversations(user_id, processed);
CREATE INDEX IF NOT EXISTS idx_user_profile_user ON user_profile(user_id, rejected);
CREATE INDEX IF NOT EXISTS idx_observations_user ON observations(user_id, rejected);
CREATE INDEX IF NOT EXISTS idx_events_user ON events(user_id);
CREATE INDEX IF NOT EXISTS idx_relationships_user ON relationships(user_id);
CREATE INDEX IF NOT EXISTS idx_user_model_user ON user_model(user_id);
CREATE INDEX IF NOT EXISTS idx_trajectory_user ON trajectory(user_id);
CREATE INDEX IF NOT EXISTS idx_strategies_user ON strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_session_tags_user ON session_tags(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_snapshot_user ON memory_snapshot(user_id);
