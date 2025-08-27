from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get("query_string", b"").decode())
        token = None
        if "token" in query:
            token = query["token"][0]
        else:
            headers = dict(scope.get("headers", []))
            auth = headers.get(b"authorization")
            if auth and auth.startswith(b"Bearer "):
                token = auth.split(b" ", 1)[1].decode()

        scope["user"] = AnonymousUser()
        if token:
            try:
                UntypedToken(token)
                jwt_auth = JWTAuthentication()
                validated = jwt_auth.get_validated_token(token)
                user = await database_sync_to_async(jwt_auth.get_user)(validated)
                scope["user"] = user
            except Exception:
                pass
        return await self.inner(scope, receive, send)