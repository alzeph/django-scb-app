from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTAuthenticationFlexible(JWTAuthentication):
    def authenticate(self, request):
        # 1. Essaye de lire depuis le cookie
        raw_token = request.COOKIES.get("access")

        # 2. Si pas dans cookie, regarde dans le header Authorization
        if not raw_token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                raw_token = auth_header.split(" ")[1]

        # 3. Aucun token trouvé
        if not raw_token:
            return None

        # 4. Valide le token
        validated_token = self.get_validated_token(raw_token)

        # 5. Retourne l'utilisateur et le token
        return self.get_user(validated_token), validated_token