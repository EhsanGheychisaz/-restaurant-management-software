from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import InvalidToken

class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        
        try:
            return super().authenticate(request=request)
        except InvalidToken:
            return None
        # header = self.get_header(request)
            
        # if header is None:
        #     raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        # else:
        #     raw_token = self.get_raw_token(header)
        # if raw_token is None:
        #     return None
        
        # validated_token = self.get_validated_token(raw_token)
    
        # return self.get_user(validated_token), validated_token