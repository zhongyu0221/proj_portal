from django import forms
from .models import Project, Task, TaskAssignment, Issue
from userprofiles.models import UserProfile
from django.forms import inlineformset_factory

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)


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
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
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


