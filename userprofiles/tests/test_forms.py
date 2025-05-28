from django.test import TestCase

from .. import forms

class UserFromTests(TestCase):
    
    def test_init(self):
        form = forms.UserForm()
        self.assertTrue(form.fields['email'].required)
