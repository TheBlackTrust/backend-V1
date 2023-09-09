from django.urls import path

from account.views import (
    RegisterUserView,
    ObtainJWTView,
    UserProfileView,
    DeleteUserProfileView,  # Changed to the DeleteUserProfileView
    get_all_users,
    get_user_by_id,
    update_user,
    delete_user,
    PasswordResetView,
    PasswordResetConfirmView,
    EmailVerificationView,
    LogoutView,
    OnboardingView
    
) 


urlpatterns = [
    path('user/register/', RegisterUserView.as_view(), name='register-user'),

    path('user/login/', ObtainJWTView.as_view(), name='obtain-jwt'),
    path('user/logout/', LogoutView.as_view(), name='logout'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('user/profile/delete/', DeleteUserProfileView.as_view(), name='delete-user'),  # Use DeleteUserProfileView here
    path('user/all/', get_all_users, name='get-all-users'),
    path('user/<int:user_id>/', get_user_by_id, name='get-user-by-id'),
    path('user/<int:user_id>/update/', update_user, name='update-user'),
    path('user/<int:user_id>/delete/', delete_user, name='delete-user'),
    path('user/password-reset/', PasswordResetView.as_view(), name='password-reset-request'),
    path('user/password-reset/confirm/<str:uid>/<str:token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path("user/email-verification/<str:uid>/<str:token>/", EmailVerificationView.as_view(), name="email-verification"),    
    path('user/onboarding/', OnboardingView.as_view(), name='onboarding'),

]
