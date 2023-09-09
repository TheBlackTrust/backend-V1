from django.shortcuts import get_object_or_404, render
from rest_framework import generics, permissions, status

from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from account.customauthorization import CookieJWTAuthentication
from account.permissions import CustomIsAuthenticated
from .models import ReportAScam, ScamStory
from .serializers import ReportAScamSerializer, ScamStorySerializer


class ReportAScamView(generics.ListCreateAPIView):
    queryset = ReportAScam.objects.all()
    serializer_class = ReportAScamSerializer
    permission_classes = [CustomIsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get_queryset(self):
        user = self.request.user

        if not user.is_active:
            raise PermissionDenied()
        elif user.is_staff or user.is_superuser:
            return ReportAScam.objects.all()
        else:
            return ReportAScam.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # This will associate the user automatically
        return Response(
            {"message": "Report created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )
    
    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(
                {"message": "Please activate your account to continue"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().handle_exception(exc)


# Report detail view for all users
class ReportAScamDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReportAScam.objects.all()
    serializer_class = ReportAScamSerializer
    permission_classes = [CustomIsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get_object(self):
        obj = get_object_or_404(self.queryset, pk=self.kwargs["pk"])
        user = self.request.user
        if not (user.is_staff or user.is_superuser) and obj.user != user:
            self.permission_denied(self.request)
        return obj

    def update(self, request, *args, **kwargs):
        action = request.data.get("action", None)

        if action == "save_for_later":
            report = self.get_object()
            report.save_for_later()
            return Response(
                {"message": "Report saved for later."}, status=status.HTTP_200_OK
            )
        elif action == "preview":
            report = self.get_object()
            report.preview()
            return Response(
                {"message": "Report set for preview."}, status=status.HTTP_200_OK
            )
        elif action == "publish":
            report = self.get_object()
            report.publish()
            return Response({"message": "Report published."}, status=status.HTTP_200_OK)
        else:
            return super().update(request, *args, **kwargs)
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Report deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )



class ScamStoryView(generics.ListCreateAPIView):
    queryset = ScamStory.objects.all()
    serializer_class = ScamStorySerializer
    permission_classes = [CustomIsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get_queryset(self):
        user = self.request.user

        if not user.is_active:
            raise PermissionDenied()

        if user.is_staff or user.is_superuser:
            return ScamStory.objects.all()
        else:
            return ScamStory.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # This will associate the user automatically
        return Response(
            {"message": "Scam story created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(
                {"message": "Please activate your account to continue"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().handle_exception(exc)


# Story detail view for all users
class ScamStoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ScamStory.objects.all()
    serializer_class = ScamStorySerializer
    permission_classes = [CustomIsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get_object(self):
        # Override get_object to ensure non-staff users can only retrieve their own reports
        obj = get_object_or_404(self.queryset, pk=self.kwargs["pk"])
        user = self.request.user
        if not (user.is_staff or user.is_superuser) and obj.user != user:
            self.permission_denied(self.request)
        return obj

    def update(self, request, *args, **kwargs):
        action = request.data.get("action", None)

        if action == "save_for_later":
            story = self.get_object()
            story.save_for_later()
            return Response(
                {"message": "Story saved for later."}, status=status.HTTP_200_OK
            )
        elif action == "preview":
            Story = self.get_object()
            Story.preview()
            return Response(
                {"message": "Story set for preview."}, status=status.HTTP_200_OK
            )
        elif action == "publish":
            Story = self.get_object()
            Story.publish()
            return Response({"message": "Story published."}, status=status.HTTP_200_OK)
        else:
            return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Story deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
        



"""

# class ScamStoryView(generics.ListCreateAPIView):
#     queryset = ScamStory.objects.all()
#     serializer_class = ScamStorySerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff or user.is_superuser:
#             return ScamStory.objects.all()
#         else:
#             return ScamStory.objects.filter(user=user)

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         # Convert the serialized data to a dictionary and exclude non-serializable fields
#         data = [dict(item) for item in serializer.data]
#         return JsonResponse(data, safe=False)


# # Story detail view for all users
# class ScamStoryDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = ScamStory.objects.all()
#     serializer_class = ScamStorySerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_object(self):
#         # Override get_object to ensure non-staff users can only retrieve their own stories

#          # obj = super().get_object()
#         obj = get_object_or_404(self.queryset, pk=self.kwargs["pk"])
#         user = self.request.user
#         if not (user.is_staff or user.is_superuser) and obj.user != user:
#             self.permission_denied(self.request)
#         return obj

"""
