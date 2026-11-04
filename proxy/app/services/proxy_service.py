"""Generic async HTTP forwarding logic."""

# Headers that must not be forwarded from the upstream response to the client
# (HTTP hop-by-hop headers that only apply to a single transport link)
_HOP_BY_HOP = frozenset(
    [
        "transfer-encoding",
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "upgrade",
    ]
)

import httpx
from fastapi import Request, Response


async def forward(
    request: Request,
    target_url: str,
    extra_headers: dict[str, str] | None = None,
) -> Response:
    """
    Forward `request` to `target_url`, inject `extra_headers`, and return
    the upstream response as a FastAPI Response. The `host` header is always
    stripped so upstream services see their own hostname.
    """
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    if extra_headers:
        headers.update(extra_headers)

    async with httpx.AsyncClient() as client:
        upstream = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body(),
        )

    # Filter hop-by-hop headers before returning to the client
    response_headers = {
        k: v
        for k, v in upstream.headers.items()
        if k.lower() not in _HOP_BY_HOP
    }

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
    )
