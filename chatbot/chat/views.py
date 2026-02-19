from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import ChatLog
from .forms import RegisterForm, ProfileUpdateForm
from .nlp.chatbot_engine import generate_response, get_remaining_requests  # ✅ ADDED


def home_view(request):
    """Landing page"""
    return render(request, "home.html")


def register_view(request):
    """User registration"""
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "auth/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "auth/login.html")

    return render(request, "auth/login.html")


def logout_view(request):
    """User logout"""
    logout(request)
    return redirect("login")


@login_required
def chat_view(request):
    """Chat page (non-AJAX fallback)"""
    response = None

    if request.method == "POST":
        user_message = request.POST.get("message", "").strip()

        if not user_message:
            response = "Please type a message 😊"
        else:
            bot_response = generate_response(user_message, user=request.user)

            ChatLog.objects.create(
                user=request.user, user_message=user_message, bot_response=bot_response
            )

            response = bot_response

    remaining = get_remaining_requests(request.user)  # ✅ ADDED

    return render(request, "chat/chat.html", {
        "response": response,
        "remaining_requests": remaining  # ✅ ADDED
    })


@login_required
@require_POST
def ajax_chat_view(request):
    """AJAX chat handler (no page reload)"""
    user_message = request.POST.get("message", "").strip()

    if not user_message:
        return JsonResponse({"bot_response": "Please type a message 😊"}, status=400)

    bot_response = generate_response(user_message, user=request.user)  # ✅ ADDED user=

    ChatLog.objects.create(
        user=request.user, user_message=user_message, bot_response=bot_response
    )

    remaining = get_remaining_requests(request.user)  # ✅ ADDED

    return JsonResponse({
        "user_message": user_message,
        "bot_response": bot_response,
        "remaining_requests": remaining  # ✅ ADDED
    })


@login_required
def chat_history_view(request):
    """Display chat history"""
    chats = (
        ChatLog.objects.filter(user=request.user)
        .select_related("user")
        .order_by("-created_at")
    )

    return render(request, "chat/history.html", {"chats": chats})


@login_required
def profile_view(request):
    """Update user profile"""
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "profile.html", {"form": form})