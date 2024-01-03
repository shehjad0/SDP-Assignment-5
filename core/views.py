from django.shortcuts import render
from books.models import Book, Category

def index(request, book_category = None):
    books = Book.objects.all()
    categories = Category.objects.all()
    
    if book_category is not None:
        books = books.filter(categories=book_category)
    
    return render(request, 'index.html', {'books': books, 'categories': categories})