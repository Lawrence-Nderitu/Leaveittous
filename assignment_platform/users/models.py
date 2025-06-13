from django.db import models
from django.contrib.auth.models import AbstractUser
# settings is not used here yet, but might be if AUTH_USER_MODEL needs to be referenced by other models within this app.
# from django.conf import settings

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('writer', 'Writer'),
        ('admin', 'Admin'),
    ]
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='student',
    )
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(blank=True)

    # If you add methods that refer to other models that might cause circular imports,
    # ensure to handle them correctly, e.g. using string references for model names
    # or importing within the method.
    # For now, this model is self-contained or only references Django's built-ins.
