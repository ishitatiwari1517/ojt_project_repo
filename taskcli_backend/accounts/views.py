from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from .models import Task

def login_page(request):
    if request.user.is_authenticated:
        return redirect("/dashboard/")
    return render(request, "index.html")

def do_login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            return render(request, "index.html", {"error": "Email and password required."})

        user = authenticate(username=email, password=password)

        if user:
            login(request, user)
            return redirect("/dashboard/")
        else:
            return render(request, "index.html", {"error": "Invalid email or password."})

    return redirect("/")

def do_signup(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not name or not email or not password:
            return render(request, "index.html", {"error": "All fields required."})

        if len(password) < 6:
            return render(request, "index.html", {"error": "Password must be at least 6 characters."})

        if User.objects.filter(username=email).exists():
            return render(request, "index.html", {"error": "Email already registered."})

        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=name,
            password=password
        )
        login(request, user)
        return redirect("/dashboard/")

    return redirect("/")

@login_required(login_url="/")
@ensure_csrf_cookie
def dashboard_page(request):
    tasks = Task.objects.filter(user=request.user)
    context = {
        'tasks': tasks,
        'user_name': request.user.first_name or request.user.username
    }
    return render(request, "dashboard.html", context)

def do_logout(request):
    logout(request)
    return redirect("/")

@login_required(login_url="/")
@csrf_protect
def add_task(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        project = request.POST.get("project", "").strip()
        priority = request.POST.get("priority", "Medium").strip()
        due_date = request.POST.get("due_date", "").strip()
        due_time = request.POST.get("due_time", "").strip()

        if not name or not project or not due_date or not due_time:
            tasks = Task.objects.filter(user=request.user)
            return render(request, "dashboard.html", {
                'tasks': tasks,
                'user_name': request.user.first_name or request.user.username,
                'error': 'All fields required'
            })

        try:
            Task.objects.create(
                user=request.user,
                name=name,
                project=project,
                priority=priority,
                due_date=due_date,
                due_time=due_time,
                completed=False
            )
            return redirect("/dashboard/")
        except Exception as e:
            tasks = Task.objects.filter(user=request.user)
            return render(request, "dashboard.html", {
                'tasks': tasks,
                'user_name': request.user.first_name or request.user.username,
                'error': 'Invalid input. Please check the date and time format.'
            })
    
    return redirect("/dashboard/")

@login_required(login_url="/")
def complete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.completed = True
        task.save()
    except Task.DoesNotExist:
        pass
    return redirect("/dashboard/")

@login_required(login_url="/")
def pending_task(request, task_id):
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
    try:
        task = Task.objects.get(id=task_id, user=request.user)
    except Task.DoesNotExist:
        return redirect("/dashboard/")
    
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        project = request.POST.get("project", "").strip()
        priority = request.POST.get("priority", "Medium").strip()
        due_date = request.POST.get("due_date", "").strip()
        due_time = request.POST.get("due_time", "").strip()

        if not name or not project or not due_date or not due_time:
            tasks = Task.objects.filter(user=request.user)
            return render(request, "dashboard.html", {
                'tasks': tasks,
                'user_name': request.user.first_name or request.user.username,
                'error': 'All fields required'
            })

        try:
            task.name = name
            task.project = project
            task.priority = priority
            task.due_date = due_date
            task.due_time = due_time
            task.save()
            return redirect("/dashboard/")
        except Exception as e:
            tasks = Task.objects.filter(user=request.user)
            return render(request, "dashboard.html", {
                'tasks': tasks,
                'user_name': request.user.first_name or request.user.username,
                'error': 'Invalid input. Please check the date and time format.'
            })
    
    return redirect("/dashboard/")

@login_required(login_url="/")
def delete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.delete()
    except Task.DoesNotExist:
        pass
    return redirect("/dashboard/")
