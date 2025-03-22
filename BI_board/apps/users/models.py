from django.db import models
from django.contrib.auth.models import AbstractUser

class Users(AbstractUser):
    role = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

class ApiIntegrations(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, blank=True, null=True)
    api_name = models.CharField(max_length=255)
    api_key = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_integrations'