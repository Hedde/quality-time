"""Enable Cross Origin Resource Sharing (CORS)."""

import os

import bottle


@bottle.route('/<:re:.*>', method='OPTIONS')
def enable_cors_generic_route() -> str:
    """This route takes priority over all others. So any request with an OPTIONS
    method will be handled by this function.

    See: https://github.com/bottlepy/bottle/issues/402

    NOTE: This means we won't 404 any invalid path that is an OPTIONS request."""
    return ""


@bottle.hook('after_request')
def enable_cors_after_request_hook() -> None:
    """This executes after every route. We use it to attach CORS headers when applicable."""
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    headers = dict(
        Origin=frontend_url, Methods="GET, POST, PUT, DELETE, OPTIONS", Credentials="true",
        Headers="Origin, Accept, Content-Type, Cookie, Set-Cookie, X-Requested-With, X-CSRF-Token, Cache-Control, " \
                "Last-Event-Id")
    for key, value in headers.items():
        bottle.response.set_header(f"Access-Control-Allow-{key}", value)
