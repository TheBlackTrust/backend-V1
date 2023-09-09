from rest_framework.exceptions import APIException
from rest_framework import status


class RegistrationFailed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {"Registration failed": "please input valid data in every fields"}
    default_code = "registration_failed"


class AuthenticationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = {"invalid credentials": "please input a valid data"}
    default_code = "authentication_failed"
