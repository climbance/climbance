from typing import Annotated

from fastapi import Depends, HTTPException, Request

from climb.log import app_user_of, authored, user_of
from climb.storage import Database

# the cookie a signed-in browser carries its session's token in
SESSION_COOKIE = "session"
# the addresses only a request from this machine arrives at
LOOPBACK = {"127.0.0.1", "::1"}


def _root(request: Request) -> Database:
    return request.app.state.root


Root = Annotated[Database, Depends(_root)]


def bearer_of(request: Request) -> str | None:
    """The app's token where the request carries one."""
    scheme, _, token = request.headers.get("authorization", "").partition(" ")
    return token if scheme.lower() == "bearer" and token else None


def _user_id(request: Request, root: Root) -> str:
    # an app's bearer token or the pages' session, read on every request, so a
    # revoked one ends at once. Each reaches every route: `api/app-tokens.md`
    token = bearer_of(request)
    if token:
        user_id = app_user_of(root, token)
    else:
        cookie = request.cookies.get(SESSION_COOKIE)
        user_id = user_of(root, cookie) if cookie else None
    if user_id is None:
        raise HTTPException(401, "not signed in")
    return user_id


UserId = Annotated[str, Depends(_user_id)]


def on_loopback(request: Request) -> bool:
    # the address the request arrived at, which another machine's request never
    # is. Checked per request: the app is built before any address is bound
    server = request.scope.get("server")
    return server is not None and server[0] in LOOPBACK


def author(request: Request, root: Database, user_id: str) -> bool:
    # off loopback the user must also be the one `CLIMB_AUTHOR_ID` pins, which
    # no invitation can grant. The dev login answers on loopback alone, and
    # refuses to start beside a provider, so its user is the local engine's
    # author
    if on_loopback(request):
        return user_id == request.app.state.dev_user or authored(root, user_id)
    pinned = request.app.state.hosted_author
    return pinned is not None and user_id == pinned and authored(root, user_id)


def author_id(request: Request, root: Root, user_id: UserId) -> str:
    if not author(request, root, user_id):
        raise HTTPException(403, "the author pages need the author role")
    return user_id
