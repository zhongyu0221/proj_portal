import string
import random
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site

from django.views.generic import FormView
from .forms import UserProfileForm, UserForm, CustomPasswordResetForm
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


class CustomPasswordResetConfirmView(FormView):
    """Custom password reset confirm view"""
    template_name = 'userprofiles/password_reset_confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('userprofiles:userlogin')

    def dispatch(self, request, *args, **kwargs):
        self.uidb64 = kwargs.get('uidb64')
        self.token = kwargs.get('token')
        
        try:
            uid = force_str(urlsafe_base64_decode(self.uidb64))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            self.user = None
        
        if self.user is None or not default_token_generator.check_token(self.user, self.token):
            messages.error(request, "The password reset link is invalid or has expired.")
            return HttpResponseRedirect(reverse_lazy('userprofiles:userlogin'))
        
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "✅ Your password has been successfully reset. You can now sign in with your new password."
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.user
        return context

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
    """List all user profiles with pagination and view_all functionality"""
    template_name = 'userprofiles/members_list.html'
    model = UserProfile
    paginate_by = 10  # Show 10 members per page by default
    
    def get_queryset(self):
        """Get queryset with optional view_all parameter"""
        queryset = UserProfile.objects.all().order_by('-user__date_joined')
        
        # Check if view_all parameter is present
        view_all = self.request.GET.get('view_all')
        if not view_all:
            # If not view_all, limit to first 10 records
            queryset = queryset[:10]
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add additional context for the template"""
        context = super().get_context_data(**kwargs)
        
        # Add view_all status
        context['view_all'] = self.request.GET.get('view_all') == 'true'
        
        # Add total count for display
        context['total_members'] = UserProfile.objects.count()
        
        # Add pagination info
        if context['view_all']:
            context['is_paginated'] = self.get_queryset().count() > self.paginate_by
            context['page_obj'] = self.get_paginated_queryset()
        else:
            context['is_paginated'] = False
            context['page_obj'] = None
        
        return context
    
    def get_paginated_queryset(self):
        """Get paginated queryset when view_all is enabled"""
        if not self.request.GET.get('view_all'):
            return None
        
        paginator = self.get_paginator(self.get_queryset(), self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return page_obj

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
            try:
                # Create user with inactive status initially
                user = user_form.save(commit=False)
                user.is_active = True  # Set to active since admin is creating it
                user.save()
                
                # Create user profile
                profile = form.save(commit=False)
                profile.user = user
                profile.save()
                
                # Send password reset email
                try:
                    reset_form = PasswordResetForm({'email': user.email})
                    if reset_form.is_valid():
                        reset_form.save(
                            request=self.request,
                            use_https=self.request.is_secure(),
                            email_template_name='registration/password_reset_email.html',
                            subject_template_name='registration/password_reset_subject.txt'
                        )
                        messages.success(
                            self.request, 
                            f"✅ Member '{user.get_full_name() or user.username}' created successfully! "
                            f"A password setup email has been sent to {user.email}."
                        )
                    else:
                        messages.warning(
                            self.request,
                            f"⚠️ Member created but password reset email failed to send. "
                            f"Please contact {user.email} directly."
                        )
                except Exception as e:
                    messages.warning(
                        self.request,
                        f"⚠️ Member created but email delivery failed: {str(e)}. "
                        f"Please contact {user.email} directly."
                    )
                
                return HttpResponseRedirect(self.success_url)
                
            except Exception as e:
                messages.error(
                    self.request,
                    f"❌ Error creating member: {str(e)}. Please try again."
                )
                return self.form_invalid(form)
        else:
            # Display form errors
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(self.request, f"User {field}: {error}")
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


class CustomPasswordResetView(FormView):
    """Custom password reset view that requires both username and email"""
    template_name = 'userprofiles/forgot_password.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('userprofiles:userlogin')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        
        try:
            user = User.objects.get(username=username, email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Get current site
            current_site = get_current_site(self.request)
            
            # Create password reset URL
            reset_url = f"{self.request.scheme}://{current_site.domain}/reset/{uid}/{token}/"
            
            # Send email
            subject = 'Password Reset Request - Project Management System'
            message = f"""
Hello {user.get_full_name() or user.username},

You have requested a password reset for your account.

Please click the following link to reset your password:
{reset_url}

This link will expire in 24 hours.

If you did not request this password reset, please ignore this email.

Best regards,
Project Management Team
            """
            
            send_mail(
                subject,
                message,
                'noreply@projectmanagement.com',
                [email],
                fail_silently=False,
            )
            
            messages.success(
                self.request,
                f"✅ Password reset email sent to {email}. Please check your inbox and follow the instructions."
            )
            
        except User.DoesNotExist:
            messages.error(
                self.request,
                "❌ No user found with the provided username and email combination."
            )
            return self.form_invalid(form)
        except Exception as e:
            messages.error(
                self.request,
                f"❌ Error sending password reset email: {str(e)}. Please try again later."
            )
            return self.form_invalid(form)
        
        return super().form_valid(form)