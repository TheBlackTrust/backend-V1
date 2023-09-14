
from .models import User
import jwt
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication
# from django.contrib.auth.models import User  # Assuming you are using Django's User model

class HeaderJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")  # Get the token from the Authorization header

        if not token or not token.startswith("Bearer "):
            return None  # No token found, return None to indicate no authentication

        token = token.split(" ")[1]  # Extract the token from "Bearer <token>"

        try:
            # Verify and decode the token using your secret key
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

            # Retrieve the user based on the user ID in the payload
            user = User.objects.get(id=payload["id"])

            return (user, None)  # Authentication successful
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired. Please log in again.")
        except (jwt.DecodeError, User.DoesNotExist):
            raise AuthenticationFailed("Invalid credentials")
