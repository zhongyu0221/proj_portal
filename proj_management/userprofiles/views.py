import string
import random
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate

from django.views.generic import FormView
from .forms import UserProfileForm, UserForm
from .models import UserProfile, User

# from .forms import UserForm, UserProfileForm
from django.contrib import messages

from project.models import Project


#
# class UserLoginView(LoginView):
#     redirect_authenticated_user = True
#
#     def get_form(self, form_class=None):
#         form = super().get_form(form_class)
#         form.fields['username'].widget.attrs.update({'placeholder': 'BSDAD/UCHAD', })
#         return form
#
#     def form_invalid(self, form):
#         username = form.cleaned_data['username']
#         ip, _ = get_client_ip(self.request)
#         host = self.request.get_host()
#         if IPAddress(ip) in IPNetwork(settings.UCHICAGO_ISO_IPNETWORK) or ip == settings.UCHICAGO_ISO_IP:
#             pass
#         else:
#             LoginAttempt.objects.create(username=username,
#                                         source_address=ip,
#                                         hostname=host,
#                                         successful=False)
#         return super().form_invalid(form)
#
#     def form_valid(self, form):
#         username = form.cleaned_data['username']
#         ip = get_client_ip(self.request)
#         host = self.request.get_host()
#         user = form.get_user()
#         login(self.request, user)
#         LoginAttempt.objects.create(
#             username=username,
#             source_address=ip,
#             hostname=host,
#             successful=True,
#             user=user,
#             session_id=self.request.session.session_key
#         )
#         return HttpResponseRedirect(self.get_success_url())
#
#
# class UserProfileListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
#     template_name = "userprofiles/userprofile_list.html"
#     queryset = UserProfile.objects.all()
#     permission_required = "userprofiles.add_userprofile"
#
#
# class UserProfileDetailView(LoginRequiredMixin, DetailView):
#     queryset = UserProfile.objects.all()
#     slug_field = 'user__username'
#     template_name = 'userprofiles/userprofile_detail.html'
#
#
# class UserUpdateView(LoginRequiredMixin, UpdateView):
#     model = User
#     form_class = UserForm
#
#
# class UserProfileCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
#     model = UserProfile
#     form_class = UserProfileForm
#     permission_required = "userprofiles.add_userprofile"
#
#     def get_success_url(self):
#         return reverse("userprofiles:userprofiles_list")
#
#     def get_context_data(self, **kwargs):
#         context = super(UserProfileCreateView, self).get_context_data(**kwargs)
#
#         context['user_form'] = UserForm(
#             data=self.request.POST or None
#         )
#         return context
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         user_form = context['user_form']
#         if user_form.is_valid():
#             user = user_form.save(commit=False)
#             user.username = form.cleaned_data['bsd_id']
#             try:
#                 user.save()
#             except IntegrityError:
#                 form.add_error('bsd_id', "Duplicate BSD/UCHAD ID")
#                 return self.form_invalid(form)
#             user_profile = form.save(commit=False)
#             user_profile.user = user
#             user_profile.save()
#             self.object = user_profile
#             messages.success(self.request, "User created successfully")
#             return HttpResponseRedirect(self.get_success_url())
#
#         return self.form_invalid(form)
#
#
# class UserProfileUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
#     model = UserProfile
#     slug_field = 'user__username'
#     slug_url_kwarg = 'username'
#     form_class = UserProfileForm
#     permission_required = "userprofiles.add_userprofile"
#
#     def get_success_url(self):
#         return reverse("userprofiles:userprofiles_list")
#
#     def get_context_data(self, **kwargs):
#         context = super(UserProfileUpdateView, self).get_context_data(**kwargs)
#         user = self.object.user
#         initial = {'first_name': user.first_name,
#                    'last_name': user.last_name,
#                    'username': user.username}
#
#         context['user_form'] = UserForm(
#             initial=initial,
#             data=self.request.POST or None,
#             instance=user
#         )
#         return context
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         user_form = context['user_form']
#         if user_form.is_valid():
#             user = user_form.save()
#             user.username = form.cleaned_data['bsd_id']
#             user.save()
#             messages.success(self.request, "User information updated successfully")
#         return super(UserProfileUpdateView, self).form_valid(form)

# This is the user dashboard


class HomeView(TemplateView):
    """Generate the home page dashboard
    """
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        members_count = UserProfile.objects.count()
        projects_count = Project.objects.count()
        context['members_count'] = members_count
        context['projects_count'] = projects_count
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
            messages.success(self.request, f"Member created successfully! User name is {user.username}. ")
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