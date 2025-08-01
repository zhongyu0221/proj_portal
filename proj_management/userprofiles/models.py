from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    TECHNOLOGIST = 'TECH'
    MANAGER = 'MS'
    DIRECTOR = 'D'
    SUPERADMIN = 'SA'
    USER_LEVEL_CHOICES = (
        (TECHNOLOGIST, 'Technologist'),
        (MANAGER, 'Manager/supervisor'),
        (DIRECTOR, 'Director'),
        (SUPERADMIN, 'Super Admin'),

    )
    user_level = models.CharField(max_length=4,
                                  choices=USER_LEVEL_CHOICES,
                                  default=TECHNOLOGIST, verbose_name="role")
    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ('user__last_name', 'user__first_name')

    @property
    def last_name(self):
        return self.user.last_name

    def get_full_name(self):
        return self.user.get_full_name()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile object when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile object when the User is saved"""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()