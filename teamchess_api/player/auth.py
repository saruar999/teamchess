from urllib.parse import parse_qs
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework.authentication import TokenAuthentication as DjangoTokenAuthentication, exceptions


class TokenAuthentication(DjangoTokenAuthentication):
    """
    Overriding the TokenAuthentication class, to add a method that can be called to generate a token given a player,
    also removing the is_active check during the authentication process, because Player instances don't have a
    is_active property
    """

    def generate_token(self, player):
        token, created = self.get_model().objects.get_or_create(user=player)
        return token

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        return token.user, token


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
