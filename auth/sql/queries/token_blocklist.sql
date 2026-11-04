-- name: AddToBlocklist :exec
INSERT INTO token_blocklist (token_jti)
VALUES ($1)
ON CONFLICT (token_jti) DO NOTHING;

-- name: IsTokenBlocked :one
SELECT EXISTS (
    SELECT 1 FROM token_blocklist WHERE token_jti = $1
) AS blocked;
