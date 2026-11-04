-- name: GetUserByUsername :one
SELECT id, username, email, password_hash, created_at, updated_at
FROM users
WHERE username = $1;

-- name: GetUserById :one
SELECT id, username, email, password_hash, created_at, updated_at
FROM users
WHERE id = $1;
