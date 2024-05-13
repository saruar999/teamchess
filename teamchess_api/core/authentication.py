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
