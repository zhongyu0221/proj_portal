from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db import transaction

from faker import Faker

from orders.tests.mixins import TestOrderTestMixin
from .. import models, forms

fake = Faker()

class UserLoginViewTests(TestOrderTestMixin, TestCase):
        
    def test_get_form(self):
        response = self.client.get(settings.LOGIN_URL)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form.fields['username'].widget.attrs['placeholder'], 'BSDAD/UCHAD')

    def test_form_invalid(self):
        data = {
            'username': 'invaliduser',
            'password': 'pwd',
        }
        response = self.client.post(settings.LOGIN_URL, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(models.LoginAttempt.objects.filter(username='invaliduser', successful=False).exists())
    
    def test_form_valid(self):
        data = {
            'username': 'john',
            'password': 'mypwd',
        }
        response = self.client.post(settings.LOGIN_URL, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)
        self.assertTrue(models.LoginAttempt.objects.filter(username='john', successful=True).exists())
      
         
class UserProfileCreateViewTests(TestOrderTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user_admin = models.User.objects.create_user('useradmin', 'useradmin@thebeatles.com', 'mypwd', first_name='User')  
        self.userprofile_user_admin = models.UserProfile.objects.create(user=self.user_admin,
                                                                        bsd_id='mybsdid2',
                                                                        user_level=models.UserProfile.PATHOLOGIST)        
        content_type = ContentType.objects.get_for_model(models.UserProfile)
        permission = Permission.objects.get(codename='add_userprofile',
                                            content_type=content_type)       
        self.user_admin.user_permissions.add(permission)
        self.user_admin.save()
        self.new_profile_url = reverse('userprofiles:userprofiles_new')
        
    def test_not_logged_in_user_redirect_to_login_page(self):
        response = self.client.get(self.new_profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, settings.LOGIN_URL + f'?next={self.new_profile_url}')
    
    def test_user_with_no_permission_redirect_to_login_page(self):
        self.client.login(username=self.user.username, password='mypwd')
        self.assertFalse(self.user.has_perm('userprofiles.add_userprofile'))
        self.assertEqual(self.new_profile_url, '/userprofiles/new/')
        response = self.client.get(self.new_profile_url)
        self.assertEqual(response.status_code, 403)        

        
    def test_logged_in_user_with_permission(self):
        self.client.login(username='useradmin', password='mypwd')
        self.assertTrue(self.user_admin.has_perm('userprofiles.add_userprofile'))
        response = self.client.get(self.new_profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['user_form'], forms.UserForm)
        
    def test_form_valid_with_invalid_user_form(self):
        data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': '',
            'bsd_id': fake.pystr(),
            'user_level': models.UserProfile.ADMIN,
        }
        self.client.login(username='useradmin', password='mypwd')
        response = self.client.post(self.new_profile_url, data)
        form = response.context['form']
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertFalse(response.context['user_form'].is_valid())
    
    def test_form_valid_with_valid_user_form(self):
        data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'bsd_id': fake.pystr(),
            'user_level': models.UserProfile.ADMIN,
        }
        self.client.login(username='useradmin', password='mypwd')
        response = self.client.post(self.new_profile_url, data)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("userprofiles:userprofiles_list"))
    
    def test_form_valid_with_valid_user_form_but_duplicate_bsd_id(self):
        data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'bsd_id': 'mybsdid',
            'user_level': models.UserProfile.ADMIN,
        }
        self.client.login(username='useradmin', password='mypwd')
        response = self.client.post(self.new_profile_url, data)
        
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form.errors, {'bsd_id': ['This BSD_ID hase been used!']}, form.errors)
    
    def test_form_valid_with_valid_user_form_but_duplicate_bsd_id2(self):
        data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'bsd_id': 'john',
            'user_level': models.UserProfile.ADMIN,
        }
        self.client.login(username='useradmin', password='mypwd')
        try:
            with transaction.atomic():
                response = self.client.post(self.new_profile_url, data)
                self.assertEqual(response.status_code, 200)
                form = response.context['form']
                self.assertEqual(form.errors, {'bsd_id': ['This BSD_ID hase been used!']}, form.errors)                
        except:
            pass


class UserProfileUpdateViewTests(TestOrderTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user_admin = models.User.objects.create_user('useradmin', 'useradmin@thebeatles.com', 'mypwd', first_name='User')  
        self.userprofile_user_admin = models.UserProfile.objects.create(user=self.user_admin,
                                                                        bsd_id='mybsdid2',
                                                                        user_level=models.UserProfile.PATHOLOGIST)        
        content_type = ContentType.objects.get_for_model(models.UserProfile)
        permission = Permission.objects.get(codename='add_userprofile',
                                            content_type=content_type)       
        self.user_admin.user_permissions.add(permission)
        self.user_admin.save()
        self.update_profile_url = reverse('userprofiles:userprofiles_update', kwargs={'username': self.user.username,})
    
    def test_not_logged_in_user_redirect_to_login_page(self):
        response = self.client.get(self.update_profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, settings.LOGIN_URL + f'?next={self.update_profile_url}')
    
    def test_user_with_no_permission_redirect_to_login_page(self):
        self.client.login(username=self.user.username, password='mypwd')
        self.assertFalse(self.user.has_perm('userprofiles.add_userprofile'))
        response = self.client.get(self.update_profile_url)
        self.assertEqual(response.status_code, 403)        
       
    def test_logged_in_user_with_permission(self):
        self.client.login(username='useradmin', password='mypwd')
        self.assertTrue(self.user_admin.has_perm('userprofiles.add_userprofile'))
        response = self.client.get(self.update_profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['user_form'], forms.UserForm)
        
    def test_form_valid_with_valid_data(self):
        self.client.login(username='useradmin', password='mypwd')
        response = self.client.get(self.update_profile_url)
        self.assertEqual(response.status_code, 200)
        data = response.context['user_form'].initial
        instance = response.context['object']
        data.update({
            'bsd_id': instance.bsd_id,
            'user_level': models.UserProfile.LABTECH,
        })
        response_post = self.client.post(self.update_profile_url, data)
        self.assertEqual(response_post.status_code, 302)
        self.assertRedirects(response_post, reverse("userprofiles:userprofiles_list"))
        self.user = models.User.objects.get(pk=self.user.id)
        self.assertEqual(self.user.userprofile.user_level, models.UserProfile.LABTECH)


class UserPreferenceUpdateViewTests(TestOrderTestMixin, TestCase):
    def test_get_object(self):
        self.client.login(username='john', password='mypwd')
        response = self.client.get(reverse('userprofiles:userpreference_update'))
        self.assertEqual(response.status_code, 200)
   