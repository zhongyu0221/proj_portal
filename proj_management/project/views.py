from django.shortcuts import render
from common.views import AjaxCreateView, AjaxUpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import *
from .forms import *

from django.views.generic import CreateView, UpdateView, DeleteView,ListView

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
        return Project.objects.all().order_by('-created_at')

class ProjectCardView(ListView):
    model = Project
    template_name = 'project_card_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.all().order_by('-created_at')



class TaskCreateView(AjaxCreateView):
    model = Task
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = '/tasks/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['assignment_formset'] = TaskAssignmentFormSet(self.request.POST)
        else:
            context['assignment_formset'] = TaskAssignmentFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        assignment_formset = context['assignment_formset']
        if assignment_formset.is_valid():
            self.object = form.save()
            assignment_formset.instance = self.object
            assignment_formset.save()
            return render(self.request, 'item_edit_success.html',
                          {'item': self.object, 'action': 'created'})
        else:
            return self.form_invalid(form)

class TaskUpdateView(AjaxUpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'project/task_form.html'
    success_url = '/tasks/'

    def form_valid(self, form):
        self.object = form.save()
        return render(self.request, 'item_edit_success.html',
                      {'item': self.object, 'action': 'updated'})