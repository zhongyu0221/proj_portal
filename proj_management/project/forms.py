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
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['short_description'].required = True


class TaskAssignmentForm(forms.ModelForm):
    class Meta:
        model = TaskAssignment
        fields = "__all__"




TaskAssignmentFormSet = inlineformset_factory(
    Task,
    TaskAssignment,
    form=TaskAssignmentForm,
    extra=1,  # Number of empty forms to display
    can_delete=True
)