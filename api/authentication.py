from rest_framework.authentication import TokenAuthentication, get_authorization_header


class JWTTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        print("Authentication class is being executed")
        # auth = get_authorization_header(request).split()

        # if not auth or auth[0].lower() != self.keyword.lower().encode():
        #     return Authentication
        return super().authenticate(request)
