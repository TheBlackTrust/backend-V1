from datetime import date, timedelta
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from account.countryapi import CountryChoiceField
from .utils import send_verification_email
from .models import Category, User


class CategorySelectionSerializer(serializers.Serializer):
    selected_categories = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=Category.objects.all()), min_length=1, max_length=3)

class UserManagerSerializer(serializers.ModelSerializer):
    # country = CountryChoiceField()  # Use the API to fetch countries
    # confirm_password = serializers.CharField(write_only=True, required=True)

    selected_categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True, required=False)


    class Meta:
        model = User
        # fields = '__all__'
        fields = [
            "id",
            "username",
            "email",
            "role",
            "password",
            "selected_categories",
            "country",
            "is_active",
            "birth_date",
            "why_here",
        ]
        extra_kwargs = {
            #hide password from populating
            "password": {"write_only": True},
            "email": {"validators": [UniqueValidator(queryset=User.objects.all())]},
        }



    def validate_birth_date(self, value):
        current_date = date.today()
        age_limit_date = current_date - timedelta(days=18 * 365)  # 18 years * 365 days

        if value > age_limit_date or value == date(1900, 1, 1):
            raise serializers.ValidationError(self.error_messages['birth_date']['too_young'])
        return value


    # def validate_birth_date(self, value):
    #     current_date = date.today()
    #     age_limit_date = current_date - timedelta(days=18 * 365)  # 18 years * 365 days

    #     if value > age_limit_date or value == date(1900, 1, 1):
    #         raise serializers.ValidationError("You must be 18 years or older.")
    #     return value

    def create(self, validated_data):
        selected_categories = validated_data.pop('selected_categories', [])
        password = validated_data.pop("password")
        # confirm_password = validated_data.pop("confirm_password")

        # if password != confirm_password:
        #     raise serializers.ValidationError("Passwords must match.")

        #hashing the password before saving
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        user.selected_categories.set(selected_categories)

        # Send email verification to the user
        # user.is_active = False
        # user.save()

        # # Generate email verification token
        # token = default_token_generator.make_token(user)
        # uid = urlsafe_base64_encode(force_bytes(user.pk))

        # # Call the function to send the email verification link
        # send_verification_email(user.email, uid, token)
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    # uid = serializers.CharField()
    # token = serializers.CharField()
    new_password = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "why_here", "profile_picture"]

    def update(self, instance, validated_data):
        # Update the user profile
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.why_here = validated_data.get("why_here", instance.why_here)
        instance.profile_picture = validated_data.get(
            "profile_picture", instance.why_here
        )
        instance.save()
        return instance
