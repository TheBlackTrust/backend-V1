
import jwt
from requests import Response
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User



class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get("jwt")

        if not token:

            raise AuthenticationFailed("You are not logged in.")

        try:
            # Verify and decode the token using your secret key
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

            # Retrieve the user based on the user ID in the payload
            user = User.objects.get(id=payload["id"])

            return (user, None)  # Authentication successful
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired. Please log in again.")
        except (jwt.DecodeError, User.DoesNotExist):
            raise AuthenticationFailed(
                "You are not logged in."
            )
