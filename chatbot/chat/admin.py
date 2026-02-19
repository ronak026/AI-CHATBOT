from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ChatLog, KnowledgeBase


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin configuration
    """

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("avatar",)}),
    )

    list_display = ("username", "email", "is_staff", "is_active")
    search_fields = ("username", "email")


@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    """
    Admin configuration for chat history
    """

    list_display = ("user", "created_at")
    search_fields = ("user__username", "user_message", "bot_response")
    list_filter = ("created_at",)


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ("question_display", "question", "is_verified", "created_at")
    list_filter = ("is_verified", "created_at")
    search_fields = ("question", "question_display", "answer")
    list_editable = ("is_verified",)
    readonly_fields = ("created_at",)
    
    # ✅ FIXED: Removed invalid 'rows' parameter
    fieldsets = (
        ("Question Details", {
            "fields": ("question_display", "question")
        }),
        ("Answer", {
            "fields": ("answer",),
            # 'rows' is NOT a valid fieldset option
        }),
        ("Status", {
            "fields": ("is_verified", "created_at"),
            "classes": ("collapse",)
        })
    )
