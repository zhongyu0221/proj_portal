from django.shortcuts import render
from common.views import AjaxCreateView, AjaxUpdateView
from .models import *
from .forms import *

from django.views.generic import CreateView, UpdateView, DeleteView

class ProjectCreateView(AjaxCreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_create.html'
    success_url = '/projects/'

    def form_valid(self, form):
        self.object = form.save()
        return render(self.request, 'item_edit_success.html',
                      {'item': self.object, 'action': 'created'})

class ProjectUpdateView(AjaxUpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project/project_create.html'
    success_url = '/projects/'

    def form_valid(self, form):
        self.object = form.save()
        return render(self.request, 'item_edit_success.html',
                      {'item': self.object, 'action': 'updated'})

class TaskCreateView(AjaxCreateView):
    model = Task
    form_class = TaskForm
    template_name = 'project/task_form.html'
    success_url = '/tasks/'

    def form_valid(self, form):
        self.object = form.save()
        return render(self.request, 'item_edit_success.html',
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