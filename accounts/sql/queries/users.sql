-- name: CreateUser :one
INSERT INTO users (username, email, password_hash)
VALUES ($1, $2, $3)
RETURNING id, username, email, password_hash, created_at, updated_at;

-- name: GetUserById :one
SELECT id, username, email, password_hash, created_at, updated_at
FROM users WHERE id = $1;

-- name: UpdateUserEmail :one
UPDATE users
SET email = $2, updated_at = now()
WHERE id = $1
RETURNING id, username, email, password_hash, created_at, updated_at;

-- name: UpdateUserPassword :exec
UPDATE users
SET password_hash = $2, updated_at = now()
WHERE id = $1;

-- name: DeleteUser :exec
DELETE FROM users WHERE id = $1;
