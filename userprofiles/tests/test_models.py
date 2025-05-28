from django.test import TestCase

from .. import models
from . import factories

class UserProfileTests(TestCase):
    def setUp(self):
        self.user_profile = factories.UserProfileFactory()

    def test_str(self):
        self.assertEqual(str(self.user_profile), self.user_profile.user.get_full_name())

    def test_first_name(self):
        self.assertEqual(self.user_profile.first_name, self.user_profile.user.first_name)

    def test_last_name(self):
        self.assertEqual(self.user_profile.last_name, self.user_profile.user.last_name)

    def test_get_full_name(self):
        self.assertEqual(self.user_profile.get_full_name(), self.user_profile.user.get_full_name())
    
    def test_is_admin(self):
        self.user_profile.user_level = models.UserProfile.ADMIN
        self.assertTrue(self.user_profile.is_admin())
        self.user_profile.user_level = models.UserProfile.LABTECH
        self.assertFalse(self.user_profile.is_admin())
    
    def test_is_superadmin(self):
        self.user_profile.user_level = models.UserProfile.SUPERADMIN
        self.assertTrue(self.user_profile.is_superadmin())
        self.user_profile.user_level = models.UserProfile.LABTECH
        self.assertFalse(self.user_profile.is_superadmin())
 
    def test_is_pathologist(self):
        self.user_profile.user_level = models.UserProfile.PATHOLOGIST
        self.assertTrue(self.user_profile.is_pathologist())
        self.user_profile.user_level = models.UserProfile.LABTECH
        self.assertFalse(self.user_profile.is_pathologist())
 
    def test_is_labtech(self):
        self.user_profile.user_level = models.UserProfile.LABTECH
        self.assertTrue(self.user_profile.is_labtech())
        self.user_profile.user_level = models.UserProfile.INFORMATICIAN
        self.assertFalse(self.user_profile.is_labtech())
 
    def test_is_bioinformatician(self):
        self.user_profile.user_level = models.UserProfile.INFORMATICIAN     
        self.assertTrue(self.user_profile.is_bioinformatician())
        self.user_profile.user_level = models.UserProfile.ADMIN
        self.assertFalse(self.user_profile.is_bioinformatician())
 
    def test_is_fellow(self):
        self.user_profile.user_level = models.UserProfile.FELLOW
        self.assertTrue(self.user_profile.is_fellow())
        self.user_profile.user_level = models.UserProfile.INFORMATICIAN
        self.assertFalse(self.user_profile.is_fellow())
         
    def test_is_resident(self):
        self.user_profile.user_level = models.UserProfile.RESIDENT
        self.assertTrue(self.user_profile.is_resident())
        self.user_profile.user_level = models.UserProfile.ADMIN
        self.assertFalse(self.user_profile.is_resident())

    def test_is_genetic_analyst(self):
        self.user_profile.user_level = models.UserProfile.GENETIC_ANALYST
        self.assertTrue(self.user_profile.is_genetic_analyst())
        self.user_profile.user_level = models.UserProfile.INFORMATICIAN
        self.assertFalse(self.user_profile.is_genetic_analyst())


class LoginAttemptTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = models.User.objects.create_user('john', 'lennon@thebeatles.com', 'mypwd', first_name='John')  
        cls.userprofile = models.UserProfile.objects.create(user=cls.user,
                                                            bsd_id='mybsdid',
                                                            user_level=models.UserProfile.PATHOLOGIST)
    def test_save(self):
        login_attempt = models.LoginAttempt(
            username='mytest',
            user=None,
            source_address="127.0.0.0"
        )
        login_attempt.save()
        self.assertFalse(login_attempt.user_repr)
        
        login_attempt = models.LoginAttempt(
            username=self.user.username,
            user=self.user,
            source_address="127.0.0.0"
        )
        login_attempt.save()     
        self.assertEqual(login_attempt.user_repr, self.user.username)
    
    def test_str(self):
        login_attempt = models.LoginAttempt(
            username=self.user.username,
            user=self.user,
            source_address="127.0.0.0"
        )
        login_attempt.save()
        self.assertEqual(
            str(login_attempt),
            f'{login_attempt.username} at {login_attempt.timestamp} from {login_attempt.source_address}'
        )

        
class UserPreferenceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = models.User.objects.create_user('john', 'lennon@thebeatles.com', 'mypwd', first_name='John')  
        cls.userprofile = models.UserProfile.objects.create(user=cls.user,
                                                            bsd_id='mybsdid',
                                                            user_level=models.UserProfile.PATHOLOGIST)
    def test_str(self):
        preference = factories.UserPreferenceFactory()
        self.assertEqual(str(preference), f"{preference.user}'s preference")