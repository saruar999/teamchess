from urllib.parse import parse_qs
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async


class RoomWebSocketAuthentication:
    token_class = Token

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope["query_string"]
        query_params = query_string.decode()
        query_dict = parse_qs(query_params)
        if 'token' not in query_dict:
            user = AnonymousUser()
        else:
            token = query_dict["token"][0]
            user = await self.return_user(token)
        
        scope["user"] = user
        return await self.app(scope, receive, send)

    @database_sync_to_async
    def return_user(self, token):
        try:
            return self.token_class.objects.get(key=token).user
        except self.token_class.DoesNotExist:
            return AnonymousUser()
