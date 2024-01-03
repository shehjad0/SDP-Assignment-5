from django.urls import path
from .views import BookDetailsView, borrow_book, return_book, review_book


urlpatterns = [
    path('details/<int:pk>/', BookDetailsView.as_view(), name='book_details'),
    path('borrow/<int:pk>/', borrow_book, name='borrow_book'),
    path('return/<int:pk>/', return_book, name='return_book'),
    path('review/<int:pk>/', review_book, name='review_book'),
]