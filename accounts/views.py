from django.shortcuts import render
from django.views.generic import FormView
from .forms import UserRegistrationForm,UserUpdateForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.shortcuts import redirect
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.mixins import LoginRequiredMixin
from books.models import BorrowList

class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile')
    
    def form_valid(self,form):
        print(form.cleaned_data)
        user = form.save()
        login(self.request, user)
        print(user)
        return super().form_valid(form)
    

class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')

class UserLogoutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('home')


class UserLibraryAccountUpdateView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, self.template_name, {'form': form})

class ChangePasswordView(PasswordChangeView):
    template_name = 'accounts/change_password.html'
    
    success_url = reverse_lazy('profile')
    
    def form_valid(self,form):
        response = super().form_valid(form)
        messages.success(
                self.request,
                f"Your Password Successfully Changed")
        
        message = render_to_string("accounts/change_password_email.html", { 'user' : self.request.user })
        send_email = EmailMultiAlternatives("Change Password", '', to=[self.request.user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()
        
        return super().form_valid(form)

class BorrowingHistoryView(LoginRequiredMixin,View):
    template_name = 'accounts/borrowing_history.html'

    def get(self, request):
        borrowed_books = BorrowList.objects.filter(user=request.user, returned_date__isnull=True)
        borrowing_history = BorrowList.objects.filter(user=request.user).order_by('-borrowing_date')
        
        return render(request, self.template_name, {'user': request.user, 'books': borrowing_history})