from django import forms
from .models import Project, Task, TaskAssignment, Issue
from userprofiles.models import UserProfile
from django.forms import inlineformset_factory

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Provide a detailed description of your project, including objectives, scope, requirements, and any other relevant information...'}),
            'project_category': forms.Select(attrs={'class': 'form-select'}),
            'created_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter client name'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0'}),
            'files': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif,.zip,.rar'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        
        # Set initial values for new projects
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['created_at'].initial = timezone.now()
        
        # Make title required
        self.fields['title'].required = True


class TaskForm(forms.ModelForm):
    assigned_users = forms.ModelMultipleChoiceField(
        queryset=UserProfile.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign Users"
    )

    class Meta:
        model = Task
        fields = ['project', 'title', 'description', 'priority', 'status', 'files', 'due_date', 'completed']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter task title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the task'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'files': forms.FileInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = True
        # 设置默认值
        if not self.instance.pk:  # 新建任务时
            self.fields['status'].initial = 'TODO'
            self.fields['priority'].initial = 'MEDIUM'


class TaskAssignmentForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=UserProfile.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign Users"
    )

    class Meta:
        model = TaskAssignment
        fields = "__all__"


