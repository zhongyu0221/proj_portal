from django.db import models
from django.contrib.auth.models import User

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