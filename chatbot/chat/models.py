from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
import datetime

class User(AbstractUser):
    
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.png',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.username


class ChatLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_logs'
    )
    user_message = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


class KnowledgeBase(models.Model):
    question = models.TextField(unique=True)  # Cleaned version for matching
    question_display = models.TextField()  # Original question for display
    answer = models.TextField()
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_display[:50]
    

class UserRequestLimit(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    request_count = models.IntegerField(default=0)
    last_reset = models.DateField(default=datetime.date.today)  # ✅ FIXED

    def reset_if_new_day(self):
        today = timezone.now().date()
        if self.last_reset < today:
            self.request_count = 0
            self.last_reset = today
            self.save()

    def can_make_request(self):
        self.reset_if_new_day()
        return self.request_count < 20

    def increment(self):
        self.request_count += 1
        self.save()