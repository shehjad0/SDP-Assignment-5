
from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserLogoutView, UserLibraryAccountUpdateView, ChangePasswordView, BorrowingHistoryView
 
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserLibraryAccountUpdateView.as_view(), name='profile'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('borrowing_history/', BorrowingHistoryView.as_view(), name='borrowing_history'),
]