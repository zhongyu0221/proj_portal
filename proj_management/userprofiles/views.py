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

from project.models import Project, Task
import datetime
from django.utils import timezone
from django.db import models


class HomeView(TemplateView):
    """Generate the home page dashboard
    """
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        members_count = UserProfile.objects.count()
        projects_count = Project.objects.count()
        projects = Project.objects.all()[:5]  # Get the first 5 projects
        
        # Task status statistics
        total_tasks = Task.objects.count()
        todo_tasks = Task.objects.filter(status='TODO').count()
        in_progress_tasks = Task.objects.filter(status='IN_PROGRESS').count()
        review_tasks = Task.objects.filter(status='REVIEW').count()
        completed_tasks = Task.objects.filter(status='COMPLETED').count()
        cancelled_tasks = Task.objects.filter(status='CANCELLED').count()
        
        # Project category statistics
        exploring_projects = Project.objects.filter(project_category='EXPLORING').count()
        research_projects = Project.objects.filter(project_category='RESEARCH').count()
        development_projects = Project.objects.filter(project_category='DEVELOPMENT').count()
        testing_projects = Project.objects.filter(project_category='TESTING').count()
        deployment_projects = Project.objects.filter(project_category='DEPLOYMENT').count()
        maintenance_projects = Project.objects.filter(project_category='MAINTENANCE').count()
        other_projects = Project.objects.filter(project_category='OTHER').count()
        
        # Project status trend for the past year (quarterly data points)
        today = timezone.now().date()
        
        # Generate quarterly dates for the past year (4 data points)
        quarterly_dates = []
        quarterly_labels = []
        
        for i in range(4):
            # Calculate date for each quarter (3 months back from today)
            quarter_date = today - datetime.timedelta(days=(i * 90))  # 90 days = ~3 months
            quarterly_dates.append(quarter_date)
            # Format label as "Q1 2024", "Q2 2024", etc.
            quarter_num = 4 - i  # Reverse order: Q4, Q3, Q2, Q1
            year = quarter_date.year
            quarterly_labels.append(f"Q{quarter_num} {year}")
        
        # Reverse to show chronological order (oldest to newest)
        quarterly_dates.reverse()
        quarterly_labels.reverse()
        
        active_counts = []
        completed_counts = []
        overdue_counts = []
        
        for quarter_date in quarterly_dates:
            # Active: projects with deadline >= quarter_date and not completed
            active = Project.objects.filter(
                deadline__date__gte=quarter_date,
                deadline__isnull=False
            ).exclude(
                tasks__status='COMPLETED'
            ).distinct().count()
            
            # Completed: projects with all tasks completed by quarter_date
            completed = Project.objects.filter(
                deadline__date__lte=quarter_date,
                deadline__isnull=False
            ).filter(
                tasks__status='COMPLETED'
            ).distinct().count()
            
            # Overdue: projects with deadline < quarter_date and not completed
            overdue = Project.objects.filter(
                deadline__date__lt=quarter_date,
                deadline__isnull=False
            ).exclude(
                tasks__status='COMPLETED'
            ).distinct().count()
            
            active_counts.append(active)
            completed_counts.append(completed)
            overdue_counts.append(overdue)
        
        context['project_status_trend'] = {
            'dates': quarterly_labels,
            'active': active_counts,
            'completed': completed_counts,
            'overdue': overdue_counts,
        }
        context['members_count'] = members_count
        context['projects_count'] = projects_count
        context['projects'] = projects
        context['total_tasks'] = total_tasks
        context['todo_tasks'] = todo_tasks
        context['in_progress_tasks'] = in_progress_tasks
        context['review_tasks'] = review_tasks
        context['completed_tasks'] = completed_tasks
        context['cancelled_tasks'] = cancelled_tasks
        context['exploring_projects'] = exploring_projects
        context['research_projects'] = research_projects
        context['development_projects'] = development_projects
        context['testing_projects'] = testing_projects
        context['deployment_projects'] = deployment_projects
        context['maintenance_projects'] = maintenance_projects
        context['other_projects'] = other_projects
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