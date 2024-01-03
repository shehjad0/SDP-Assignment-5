from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import  DetailView
from .models import Book, Review, BorrowList
from .forms import ReviewForm
from accounts.models import UserLibraryAccount
from transactions.models import Transaction
from transactions.constants import BORROW, RETURN
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from decimal import Decimal
from django.utils import timezone

# Create your views here.

class BookDetailsView(DetailView):
    model = Book
    template_name = 'books/book_details.html'
    context_object_name = 'book'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        book = self.object
        context['reviews'] = Review.objects.filter(book=book)

        context['review_form'] = ReviewForm()

        return context

@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, id=pk)
    user = request.user

    if request.method == 'POST':
        user_account = UserLibraryAccount.objects.filter(user=user).first()
        
        if user_account.balance < book.price:
            messages.error(request, 'You do not have enough balance to borrow this book.')
            return redirect('book_details', pk=book.id)

        user_account.balance -= Decimal(str(book.price))
        user_account.save()

        Transaction.objects.create(
            account=user_account,
            amount=-book.price,
            balance_after_transaction=user_account.balance,
            transaction_type=BORROW
        )
        
        BorrowList.objects.create(
            user=user,
            book=book,
        )
        
        message = render_to_string("books/borrow_book_email.html", { 'user' : user, 'book' : book })
        send_email = EmailMultiAlternatives("Book Borrow Confirmation", '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()

        book.borrowers.add(user)
        messages.success(request, 'Book borrowed successfully!')
        return redirect('book_details', pk=book.id)

    return redirect('home')
    
@login_required
def return_book(request, pk):
    book = get_object_or_404(Book, id=pk)
    user = request.user
    
    next_url = request.GET.get('next', 'home')

    if request.method == 'POST':
        user_account = UserLibraryAccount.objects.filter(user=user).first()

        user_account.balance += Decimal(str(book.price))
        user_account.save()

        Transaction.objects.create(
            account=user_account,
            amount=+book.price,
            balance_after_transaction=user_account.balance,
            transaction_type=RETURN
        )
        
        borrow_instance = BorrowList.objects.get(user=user, book=book, returned_date__isnull=True)
        borrow_instance.returned_date = timezone.now()
        borrow_instance.save()

        book.borrowers.remove(user)
        messages.success(request, 'Book returned successfully!')
        return redirect(next_url)

    return redirect('home')

@login_required
def review_book(request, pk):
    book = get_object_or_404(Book, id=pk)
    user = request.user

    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.user = user
            new_review.book = book
            new_review.save()

            messages.success(request, 'Review added successfully.')
            return redirect('book_details', pk=book.id)
    
    return redirect('home')