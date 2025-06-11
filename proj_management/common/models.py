from django.db import models

class CommonInfo(models.Model):
    name = models.CharField(
        max_length=200, null=False, blank=False, unique=True,
        error_messages={'unique': 'This name has been used!'}
    )
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


