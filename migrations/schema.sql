-- migrations/schema.sql

-- ================================
-- USERS TABLE
-- ================================

CREATE TABLE IF NOT EXISTS users (
    user_id        BIGINT PRIMARY KEY,
    trials_left    INTEGER NOT NULL DEFAULT 0,
    vip_until      TIMESTAMP WITH TIME ZONE NULL,
    created_at     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- ================================
-- INDEXES
-- ================================

CREATE INDEX IF NOT EXISTS idx_users_vip_until
ON users (vip_until);
