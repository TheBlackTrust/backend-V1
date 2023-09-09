from rest_framework import serializers

from account.countryapi import CountryChoiceField
from .models import ReportAScam, ScamStory


class ScamStorySerializer(serializers.ModelSerializer):
    country = CountryChoiceField()  # Use the API to fetch countries

    class Meta:
        model = ScamStory
        fields = (
            "id",
            "user",
            "title",
            "description",
            "image_1",
            "image_2",
            "image_3",
            "image_4",
            "video_1",
            "video_2",
            "country",
            "state",
            "organisation",
            "website",
            "other_information",
            "sector",
            "scam_type",
            "status",
            "created_at",
            "updated_at",
            # "scam_stories",
        )
        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
        )


class ReportAScamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAScam
        fields = (
            "id",
            "user",
            "title",
            "image_1",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
        )
