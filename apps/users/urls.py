from django.urls import path

from apps.users.views import CustomTokenObtainPairView, LogoutView, RegistrationView, CustomTokenRefreshView

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('register/', RegistrationView.as_view()),
    path('refresh/', CustomTokenRefreshView.as_view()),
]
