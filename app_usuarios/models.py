from django.db import models

# Create your models here.


from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import secrets

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Token de recuperación"
        verbose_name_plural = "Tokens de recuperación"
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(48)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
        
    def is_valid(self):
        return timezone.now() < self.expires_at and not self.used
    
    def mark_as_used(self):
        self.used = True
        self.save()
    
    def __str__(self):
        return f"Token para {self.user.username} - {'Válido' if self.is_valid() else 'Expirado'}"