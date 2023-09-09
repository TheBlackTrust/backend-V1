from django.urls import path
from .views import ReportAScamView, ReportAScamDetailView, ScamStoryView, ScamStoryDetailView

urlpatterns = [
    # For all users: Retrieve their own reports and Create a new report
    path('reports/', ReportAScamView.as_view(), name='report-list-create'),
    # #create report
    # path('create-report/', ReportAScamView.as_view(), name='create-report'),

    # For staff and superusers: Retrieve, Update, and Delete a specific report. also publish.
    # With this implementation, you can send a PUT request to the reports/<int:pk>/ endpoint with the action field in the request data set to either "save_for_later", "preview", or "publish" to trigger the respective actions. If no action field is provided, it will default to the regular update behavior
    path('reports/<int:pk>/', ReportAScamDetailView.as_view(), name='report-detail'),

    # For all users: List and Create scam stories
    path('story/', ScamStoryView.as_view(), name='story-list-create'),

    # For all users: Retrieve, Update, and Delete a specific scam story
    # With this implementation, you can send a PUT request to the reports/<int:pk>/ endpoint with the action field in the request data set to either "save_for_later", "preview", or "publish" to trigger the respective actions. If no action field is provided, it will default to the regular update behavior
    path('story/<int:pk>/', ScamStoryDetailView.as_view(), name='story-detail'),


]
