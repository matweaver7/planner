-- Owned by auth. Accounts mirrors this for sqlc type generation but runs no migrations.
-- gen_random_uuid() is built-in from PostgreSQL 13+; no extension required.

CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username      VARCHAR(64)  UNIQUE NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT         NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE token_blocklist (
    token_jti  VARCHAR(36)  PRIMARY KEY,   -- JWT "jti" claim (UUID4 string)
    blocked_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);
