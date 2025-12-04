"""
Views for TaskCLI Web Application
==================================
This module contains all view functions for the web interface.
Handles authentication, task CRUD operations, and page rendering.

Author: TaskCLI Team
"""

from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from .models import Task


# =============================================================================
# AUTHENTICATION VIEWS
# =============================================================================

def login_page(request):
    """
    Render the login/signup page.
    
    If user is already authenticated, redirect to dashboard.
    Otherwise, show the login form.
    """
    if request.user.is_authenticated:
        return redirect("/dashboard/")
    return render(request, "index.html")


def do_login(request):
    """
    Handle user login form submission.
    
    Validates email and password, authenticates user,
    and redirects to dashboard on success.
    """
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        # Validate required fields
        if not email or not password:
            return render(request, "index.html", {"error": "Email and password required."})

        # Authenticate using email as username
        user = authenticate(username=email, password=password)

        if user:
            login(request, user)
            return redirect("/dashboard/")
        else:
            return render(request, "index.html", {"error": "Invalid email or password."})

    return redirect("/")


def do_signup(request):
    """
    Handle new user registration.
    
    Creates a new user account with name, email (as username), and password.
    Automatically logs in the user after successful registration.
    """
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        # Validate required fields
        if not name or not email or not password:
            return render(request, "index.html", {"error": "All fields required."})

        # Validate password length
        if len(password) < 6:
            return render(request, "index.html", {"error": "Password must be at least 6 characters."})

        # Check if email already exists
        if User.objects.filter(username=email).exists():
            return render(request, "index.html", {"error": "Email already registered."})

        # Create new user (email is used as username for simplicity)
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=name,
            password=password
        )
        
        # Auto-login after registration
        login(request, user)
        return redirect("/dashboard/")

    return redirect("/")


def do_logout(request):
    """Log out the current user and redirect to login page."""
    logout(request)
    return redirect("/")


# =============================================================================
# DASHBOARD VIEW
# =============================================================================

@login_required(login_url="/")
@ensure_csrf_cookie
def dashboard_page(request):
    """
    Render the main dashboard with user's tasks.
    
    Requires authentication. Displays all tasks belonging to the current user.
    """
    tasks = Task.objects.filter(user=request.user)
    context = {
        'tasks': tasks,
        'user_name': request.user.first_name or request.user.username
    }
    return render(request, "dashboard.html", context)


# =============================================================================
# TASK CRUD OPERATIONS
# =============================================================================

@login_required(login_url="/")
@csrf_protect
def add_task(request):
    """
    Handle new task creation.
    
    Supports recurring tasks with the following recurrence patterns:
    - none: Single task
    - daily_7: Daily for 7 days
    - daily_30: Daily for 30 days
    - weekly_4: Weekly for 4 weeks
    """
    if request.method == "POST":
        # Extract form data
        name = request.POST.get("name", "").strip()
        project = request.POST.get("project", "").strip()
        priority = request.POST.get("priority", "Medium").strip()
        due_date = request.POST.get("due_date", "").strip()
        due_time = request.POST.get("due_time", "").strip()
        recurrence = request.POST.get("recurrence", "none").strip()

        # Validate required fields
        if not name or not project or not due_date or not due_time:
            tasks = Task.objects.filter(user=request.user)
            return render(request, "dashboard.html", {
                'tasks': tasks,
                'user_name': request.user.first_name or request.user.username,
                'error': 'All fields required'
            })

        try:
            # Parse the start date
            start_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            dates_to_create = []

            # Calculate dates based on recurrence pattern
            if recurrence == 'daily_7':
                # Create task for each day for 7 days
                for i in range(7):
                    dates_to_create.append(start_date + timedelta(days=i))
            elif recurrence == 'daily_30':
                # Create task for each day for 30 days
                for i in range(30):
                    dates_to_create.append(start_date + timedelta(days=i))
            elif recurrence == 'weekly_4':
                # Create task weekly for 4 weeks
                for i in range(4):
                    dates_to_create.append(start_date + timedelta(weeks=i))
            else:
                # Single, non-recurring task
                dates_to_create.append(start_date)

            # Flag for recurring status
            is_recurring_flag = recurrence != 'none'

            # Create task(s)
            for d in dates_to_create:
                Task.objects.create(
                    user=request.user,
                    name=name,
                    project=project,
                    priority=priority,
                    due_date=d,
                    due_time=due_time,
                    completed=False,
                    is_recurring=is_recurring_flag
                )
            return redirect("/dashboard/")
            
        except Exception as e:
            # Handle date parsing or other errors
            tasks = Task.objects.filter(user=request.user)
            return render(request, "dashboard.html", {
                'tasks': tasks,
                'user_name': request.user.first_name or request.user.username,
                'error': 'Invalid input. Please check the date and time format.'
            })
    
    return redirect("/dashboard/")


@login_required(login_url="/")
def complete_task(request, task_id):
    """
    Mark a task as completed.
    
    Only allows completing tasks owned by the current user.
    """
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.completed = True
        task.save()
    except Task.DoesNotExist:
        pass  # Silently ignore if task doesn't exist or doesn't belong to user
    return redirect("/dashboard/")


@login_required(login_url="/")
def pending_task(request, task_id):
    """
    Mark a task as pending (uncomplete).
    
    Only allows modifying tasks owned by the current user.
    """
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.completed = False
        task.save()
    except Task.DoesNotExist:
        pass
    return redirect("/dashboard/")


@login_required(login_url="/")
@csrf_protect
def edit_task(request, task_id):
    """
    Edit an existing task.
    
    Updates task name, project, priority, due date, and due time.
    Only allows editing tasks owned by the current user.
    """
    try:
        task = Task.objects.get(id=task_id, user=request.user)
    except Task.DoesNotExist:
        return redirect("/dashboard/")
    
    if request.method == "POST":
        # Extract form data
        name = request.POST.get("name", "").strip()
        project = request.POST.get("project", "").strip()
        priority = request.POST.get("priority", "Medium").strip()
        due_date = request.POST.get("due_date", "").strip()
        due_time = request.POST.get("due_time", "").strip()

        # Validate required fields
        if not name or not project or not due_date or not due_time:
            tasks = Task.objects.filter(user=request.user)
            return render(request, "dashboard.html", {
                'tasks': tasks,
                'user_name': request.user.first_name or request.user.username,
                'error': 'All fields required'
            })

        try:
            # Update task fields
            task.name = name
            task.project = project
            task.priority = priority
            task.due_date = due_date
            task.due_time = due_time
            task.save()
            return redirect("/dashboard/")
        except Exception:
            tasks = Task.objects.filter(user=request.user)
            return render(request, "dashboard.html", {
                'tasks': tasks,
                'user_name': request.user.first_name or request.user.username,
                'error': 'Invalid input. Please check the date and time format.'
            })
    
    return redirect("/dashboard/")


@login_required(login_url="/")
def delete_task(request, task_id):
    """
    Delete a task.
    
    Permanently removes the task from the database.
    Only allows deleting tasks owned by the current user.
    """
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.delete()
    except Task.DoesNotExist:
        pass
    return redirect("/dashboard/")
