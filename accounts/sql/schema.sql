-- Mirrors auth/sql/schema.sql exactly. Accounts service does not own migrations.
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username      VARCHAR(64)  UNIQUE NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT         NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE token_blocklist (
    token_jti  VARCHAR(36)  PRIMARY KEY,
    blocked_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);
