from django.views.generic import TemplateView, ListView


from .models import UserProfile, User
# from .forms import UserForm, UserProfileForm



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


class UserProfileListView(ListView):
    """List all user profiles
    """
    template_name = 'userprofiles/members_list.html'
    queryset = UserProfile.objects.all()