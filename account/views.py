from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.http import HttpResponseServerError
from .customauthorization import CookieJWTAuthentication
from .utils import send_verification_email
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.generics import CreateAPIView
from .models import Category, User
from .serializers import (
    CategorySelectionSerializer,
    UserManagerSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserProfileSerializer,
)
from django.utils.encoding import force_bytes, force_str
from .customexceptionhandle import AuthenticationFailed, RegistrationFailed
from .permissions import CustomIsAuthenticated
import logging
from django.conf import settings
import jwt, datetime

# User = get_user_model()
# logging.basicConfig(filename="email_errors.log", level=logging.ERROR)


class RegisterUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserManagerSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            user.is_active = False
            user.save()

            # Generate email verification token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Call the function to send the email verification link
            send_verification_email(user.email, uid, token)

            return Response(
                "Registration successful: Please check your email to activate your account and have a better experience with blacktrust"
            )

        except ValidationError as e:
            # Handle validation errors and return them in the response
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logging.error(f"Error sending email: {e}")
            raise RegistrationFailed(str(e))


class ObtainJWTView(APIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        user = User.objects.filter(email=email).first()

        if user is None or not user.check_password(password):
            return Response(
                {
                    "detail": "Invalid credentials. Please check your email and password."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Create a payload for the JWT token
        expiration = datetime.datetime.utcnow() + settings.JWT_EXPIRATION_DELTA
        iat = datetime.datetime.utcnow()
        payload = {
            "id": user.id,
            "exp": expiration,
            "iat": iat,
        }

        # Encode the JWT token using your secret key from Django settings
        token = jwt.encode(payload, "secret", algorithm="HS256")

        response = Response({"jwt": token})

        # Set the JWT token as a cookie
        response.set_cookie(key="jwt", value=token, httponly=True)

        return response
        # return render(request, "index.html")


class OnboardingView(APIView):
    permission_classes = [CustomIsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request, *args, **kwargs):
        user = request.user

        serializer = CategorySelectionSerializer(data=request.data)
        if serializer.is_valid():
            selected_category_ids = serializer.validated_data.get("selected_categories")

            if len(selected_category_ids) > 3:
                return Response(
                    {"detail": "You can only select up to 3 categories."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            selected_categories = Category.objects.filter(id__in=selected_category_ids)

            user.selected_categories.set(selected_categories)

            return Response(
                {"message": "Categories selected successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie("jwt")

        response.data = {"message": "Logout successfully"}
        return response


class UserProfileView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [CustomIsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get_object(self):
        return self.request.user


class UpdateUserProfileView(APIView):
    permission_classes = [CustomIsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserManagerSerializer(user, data=request.data, partial=True)

        # Custom update for profile picture
        if "profile_picture" in request.FILES:
            user.profile_picture = request.FILES["profile_picture"]

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserProfileView(APIView):
    permission_classes = [CustomIsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response(
            {"message": "User profile deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


@api_view(["GET"])
@permission_classes([CustomIsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def get_all_users(request):
    if not request.user.is_active:
        return Response(
            {
                "message": "Please activate your account with the email sent to you to continue with this resource"
            },
            status=status.HTTP_403_FORBIDDEN,
        )
    elif request.user.is_staff:
        users = User.objects.all()
        serializer = UserManagerSerializer(users, many=True)
        return Response({"users-info": serializer.data}, status=status.HTTP_200_OK)
    else:
        raise PermissionDenied("You do not have permission to access this resource.")


@api_view(["GET"])
@permission_classes([CustomIsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def get_user_by_id(request, user_id):
    try:
        if not request.user.is_active:
            return Response(
                {
                    "message": "Please activate your account with the email sent to you to continue with this resource"
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        elif request.user.is_staff:
            user = User.objects.get(pk=user_id)
            serializer = UserManagerSerializer(user)
            return Response({"user-info": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "You do not have permission to access this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["PUT"])
@permission_classes([CustomIsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def update_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user.is_staff:
        serializer = UserManagerSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(
            {"message": "You do not have permission to update this user."},
            status=status.HTTP_403_FORBIDDEN,
        )


@api_view(["DELETE"])
@permission_classes([CustomIsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def delete_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user.is_staff or request.user.id == user.id:
        user.delete()
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )
    else:
        return Response(
            {"message": "You do not have permission to delete this user."},
            status=status.HTTP_403_FORBIDDEN,
        )


class EmailVerificationView(generics.GenericAPIView):
    def get(self, request, uid, token):
        try:
            # Decode the uid and convert it to a string
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                # Redirect to the email verified page or your frontend URL
                # frontend_url = "http://localhost:3000/login"
                # # return render(request,'email_verification.html')
                # return redirect(frontend_url)
                return Response("email successfully verified")
            else:
                # Redirect to the email verification failed page or your frontend URL
                # return redirect('http://localhost:3000/email-verification-failed/')
                return Response("email verification is unsuccessful")

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            # Redirect to the email verification failed page or your frontend URL
            # return redirect('http://localhost:3000/email-verification-failed/')
            return Response("email verification failed")


class PasswordResetView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            send_verification_email(email, uid, token)
        return Response(
            {"detail": "Password reset email has been sent."}, status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uid, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_password = serializer.validated_data["new_password"]
            user.set_password(new_password)
            user.save()
            # return render(request,'passwordreset.html')
            return Response(
                {"detail": "Password reset successful."}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST
            )
