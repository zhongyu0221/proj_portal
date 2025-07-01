import string
import random
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth import login, authenticate

from django.views.generic import FormView
from .forms import UserProfileForm, UserForm
from .models import UserProfile, User

# from .forms import UserForm, UserProfileForm
from django.contrib import messages

from project.models import Project



class HomeView(TemplateView):
    """Generate the home page dashboard
    """
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        members_count = UserProfile.objects.count()
        projects_count = Project.objects.count()
        projects = Project.objects.all()[:5]  # Get the first 5 projects
        context['members_count'] = members_count
        context['projects_count'] = projects_count
        context['projects'] = projects
        return context

class UserLoginView(FormView):
    template_name = 'userprofiles/sign_in.html'
    form_class = AuthenticationForm
    success_url = '/home/'

    def form_valid(self, form):
        user = form.get_user()
        print('form valid', user)
        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        print('form invalid', form.errors)
        return super().form_invalid(form)



class UserSignupView(TemplateView):
    """Generate the user signup page
    """
    template_name = 'userprofiles/sign_up.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserForm()
        return context



class UserProfileListView(ListView):
    """List all user profiles
    """
    template_name = 'userprofiles/members_list.html'
    queryset = UserProfile.objects.all()

# Create view: create User and UserProfile together
class UserProfileCreateView(CreateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'userprofiles/member_create.html'
    success_url = reverse_lazy('userprofiles:userprofile_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserForm(self.request.POST or None)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        if user_form.is_valid():
            user = user_form.save(commit=False)
            # Generate a random temporary password
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            user.set_password(temp_password)
            user.save()
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            # Send password reset email
            reset_form = PasswordResetForm({'email': user.email})
            if reset_form.is_valid():
                reset_form.save(
                    request=self.request,
                    use_https=self.request.is_secure(),
                    email_template_name='registration/password_reset_email.html'
                )
            messages.success(self.request, f"Member created! A password setup email has been sent to {user.email}.")

            return HttpResponseRedirect(self.success_url)
        return self.form_invalid(form)

# Update view: pre-populate user fields
class UserProfileUpdateView(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'userprofiles/member_create.html'
    success_url = reverse_lazy('userprofiles:userprofile_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object.user
        context['user_form'] = UserForm(self.request.POST or None, instance=user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        if user_form.is_valid():
            user_form.save()
            messages.success(self.request, "Member updated successfully!")
            return super().form_valid(form)
        return self.form_invalid(form)