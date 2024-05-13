from rest_framework.authentication import TokenAuthentication as DjangoTokenAuthentication, exceptions


class TokenAuthentication(DjangoTokenAuthentication):

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
