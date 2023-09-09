import os
import tempfile
from django.db import models
import pytz
from django.utils import timezone
from blacktrustapiv1 import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from moviepy.editor import VideoFileClip
from django.utils.translation import gettext_lazy as _
from account.countryapi import CountryChoiceField


SECTOR = (
    ("general", "General"),
    ("bank", "Bank"),
    ("job", "Job"),
    ("crypto", "Crypto"),
    ("travel", "Travels"),
    ("finance", "Finance"),
    ("crypto", "Crypto"),
    ("real_estate", "Real Estate"),
    ("banking", "Banking"),
    ("services", "Services"),
    ("education", "Education"),
    ("charity", "Charity"),
    ("products", "Products"),
    ("online_programs", "Online programs"),
    ("transportation", "Transportation"),
    ("oil_and_gas", "Oil and Gas"),
    ("music", "Music"),
    ("romance", "Romance"),
)

TYPE = (
    ("online", "Online"),
    ("offline", "Offline"),
    ("both", "Both"),
)

AUTHOR_STATUS = (
    ("draft", "Draft"),
    ("publish", "Publish"),
    ("save-for-later", "Save-For-Later"),

)

"""
# LEVEL = (
#     ('novice', 'Novice'),
#     ('verified', 'Verified'),
# )
"""

# class ScamCategory(models.Model):
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name


# HANDLE IMAGES
def upload_to(instance, filename):
    # Generate a unique filename based on the current timestamp and user ID
    extension = filename.split(".")[-1]  # Get the file extension
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")  # Current timestamp
    unique_filename = f"{timestamp}_{instance.user.id}.{extension}"

    # Return the full path to the file
    return os.path.join("scam_images/", unique_filename)


def get_default_media_image():
    # Path to the default image relative to the MEDIA_ROOT
    default_image_path = os.path.join("default/", "defaultImage.PNG")

    # Return the full path to the default image
    return os.path.join( default_image_path)


# HANDLE VIDEOS
def validate_video_duration(value):
    max_duration = 300  # Maximum duration in seconds (5 minutes)

    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
            for chunk in value.chunks():
                temp_video_file.write(chunk)

            temp_video_file_name = temp_video_file.name

        video = VideoFileClip(temp_video_file_name)
        duration = video.duration
        video.close()  # Make sure to close the video object before removing the file
        os.remove(temp_video_file_name)

        if duration > max_duration:
            raise ValidationError(
                _("Video duration should not exceed 300 seconds (5 minutes).")
            )
    except Exception as e:
        raise ValidationError(
            _("Error occurred while validating video duration: %s" % e)
        )


# Validate image file size
def validate_image_size(value):
    max_size = 10 * 1024 * 1024  # 10 MB

    if value.size > max_size:
        raise ValidationError(_("Image size should not exceed 10 MB."))


# Validate video file size
def validate_video_size(value):
    max_size = 30 * 1024 * 1024  # 30 MB

    if value.size > max_size:
        raise ValidationError(_("Video size should not exceed 30 MB."))


class ScamStory(models.Model):
    user = models.ForeignKey("account.User", on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(blank=False)
    image_1 = models.ImageField(
        upload_to=upload_to,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png"]),
            validate_image_size,
        ],
    )
    image_2 = models.ImageField(
        upload_to=upload_to,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png"]),
            validate_image_size,
        ],
    )
    image_3 = models.ImageField(
        upload_to=upload_to,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png"]),
            validate_image_size,
        ],
    )
    image_4 = models.ImageField(
        upload_to=upload_to,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png"]),
            validate_image_size,
        ],
    )
    video_1 = models.FileField(
        upload_to="scam_videos/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(["mp4", "avi", "mov"]),
            validate_video_size,
        ],
    )
    video_2 = models.FileField(
        upload_to="scam_videos/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(["mp4", "avi", "mov"]),
            validate_video_size,
        ],
    )

    country = models.CharField(
        max_length=100, choices=CountryChoiceField().get_country_choices()
    )
    state = models.CharField(max_length=100, null=False)
    organisation = models.CharField(max_length=200, null=False)
    website = models.URLField(max_length=200, blank=True, null=True)
    other_information = models.TextField(blank=True, null=True)
    sector = models.CharField(max_length=20, choices=SECTOR, null=False)
    scam_type = models.CharField(max_length=10, choices=TYPE, null=False)
    status = models.CharField(max_length=20, choices=AUTHOR_STATUS, default="draft")
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Created At",
        help_text="The date and time when this record was created.",
    )
    updated_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Updated At",
        help_text="The date and time when this record was last updated.",
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            # If the object is being created, set created_at to the current date and time in UTC
            self.created_at = timezone.now()
        # Always update updated_at to the current date and time in UTC when the object is saved
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pk} - {self.created_at:%Y-%m-%d %H:%M:%S}"

    class Meta:
        verbose_name = "ScamStory"
        verbose_name_plural = "ScamStories"

    def save_for_later(self):
        self.status = "draft"
        self.save()

    def preview(self):
        self.status = "preview"
        self.save()

    def publish(self):
        self.status = "publish"
        self.save()

    def __str__(self):
        return f"Scam Story by {self.user.username} - {self.created_at}"


class ReportAScam(models.Model):
    user = models.ForeignKey("account.User", on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(null=False)
    image_1 = models.ImageField(
        default=get_default_media_image,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png"]),
            validate_image_size,
        ],
    )
    status = models.CharField(max_length=20, choices=AUTHOR_STATUS, default="draft")
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Created At",
        help_text="The date and time when this record was created.",
    )
    updated_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Updated At",
        help_text="The date and time when this record was last updated.",
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            # If the object is being created, set created_at to the current date and time in UTC
            self.created_at = timezone.now()
        # Always update updated_at to the current date and time in UTC when the object is saved
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pk} - {self.created_at:%Y-%m-%d %H:%M:%S}"

    class Meta:
        verbose_name = "ReportAScam"
        verbose_name_plural = "ReportAScams"

    """
    # media_2 = models.ImageField(upload_to='scam_media/', blank=True, null=True)
    # media_3 = models.ImageField(upload_to='scam_media/', blank=True, null=True)
    # media_4 = models.ImageField(upload_to='scam_media/', blank=True, null=True)
    #country = CountryChoiceField(max_length=100, choices=CountryChoiceField().get_country_choices())
    # state = models.CharField(max_length=100)
    # organisation = models.CharField(max_length=200)
    # website = models.URLField(max_length=200, blank=True, null=True)
    # other_information = models.TextField(blank=True, null=True)
    # sector = models.CharField(max_length=20, choices=SECTOR)
    # scam_type = models.CharField(max_length=10, choices=TYPE)
    # status = models.CharField(max_length=20, choices=AUTHOR_STATUS, default='draft')
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # scam_channel = models.CharField(max_length=100)
    """

    def save_for_later(self):
        self.status = "draft"
        self.save()

    def preview(self):
        self.status = "preview"
        self.save()

    def publish(self):
        self.status = "publish"
        self.save()

    def __str__(self):
        return self.title
