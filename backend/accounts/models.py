from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin


class CustomUserManager(UserManager):
    def create_user(self, full_name, email, password = None, **extra_fields):
        if not email:
            raise ValueError('Email is Required')
        email=self.normalize_email(email)
        user=self.model(full_name=full_name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, full_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(full_name, email, password, **extra_fields)
        

class User(AbstractBaseUser, PermissionsMixin):
    email=models.EmailField(unique=True)

    full_name=models.CharField(max_length=255, blank=False)

    created_at=models.DateTimeField(auto_now_add=True)
    
    updated_at=models.DateTimeField(auto_now=True)
    
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    objects=CustomUserManager()

    def __str__(self):
        return self.email
    
