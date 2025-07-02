from django.shortcuts import render, get_object_or_404, redirect
from common.views import AjaxCreateView, AjaxUpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import *
from .forms import *
from django.db.models import Count

from django.views.generic import CreateView, UpdateView, DeleteView,ListView


# PROJECT
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_create.html'
    success_url = reverse_lazy('projects:project_create')


    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Project "{self.object}" created successfully.')
        return response

class ProjectUpdateView(AjaxUpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project/project_create.html'
    success_url = '/projects/'

class ProjectListView(ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.annotate(task_count=Count('tasks')).order_by('-created_at')



class ProjectCardView(ListView):
    model = Project
    template_name = 'project_card_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.annotate(task_count=Count('tasks')).order_by('-created_at')



# TASK

class TaskCreateView(AjaxCreateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = '/tasks/'

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=kwargs['project_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['project'] = self.project
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        users = form.cleaned_data.get('assigned_users')
        for user in users:
            TaskAssignment.objects.create(task=self.object, user=user, assigned_at=timezone.now())
        return render(self.request, 'common/item_edit_form_success.html',
                          {'item': self.object, 'action': 'created'})


class TaskUpdateView(AjaxUpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'project/task_form.html'
    success_url = '/tasks/'

    def form_valid(self, form):
        self.object = form.save()
        return render(self.request, 'item_edit_success.html',
                      {'item': self.object, 'action': 'updated'})