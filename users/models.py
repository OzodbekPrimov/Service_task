from django.contrib.auth.models import AbstractUser
from django.db import models

class Roles(models.TextChoices):
    CLIENT = "client", "Client"
    WORKER = "worker", "Worker"
    ADMIN = "admin", "Admin"

class ServiceType(models.TextChoices):
    PLUMBER = "plumber", "Plumber"
    ELECTRICIAN = "electrician", "Electrician"
    CLEANER = "cleaner", "Cleaner"

class User(AbstractUser):
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CLIENT)

class WorkerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="worker_profile")
    service_type = models.CharField(max_length=32, choices=ServiceType.choices)

    def __str__(self):
        return f"{self.user.username} · {self.service_type}"