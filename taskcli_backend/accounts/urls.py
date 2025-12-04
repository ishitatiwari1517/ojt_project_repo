"""
URL Configuration for TaskCLI Accounts App
===========================================
Defines all URL routes for authentication, task operations, and API.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication Routes
    path("", views.login_page, name="login"),
    path("login/", views.do_login, name="do_login"),
    path("register/", views.do_signup, name="do_signup"),
    path("logout/", views.do_logout, name="logout"),
    
    # Dashboard
    path("dashboard/", views.dashboard_page, name="dashboard"),
    
    # Task CRUD Operations
    path("add-task/", views.add_task, name="add_task"),
    path("edit-task/<int:task_id>/", views.edit_task, name="edit_task"),
    path("complete-task/<int:task_id>/", views.complete_task, name="complete_task"),
    path("pending-task/<int:task_id>/", views.pending_task, name="pending_task"),
    path("delete-task/<int:task_id>/", views.delete_task, name="delete_task"),
    
    # API Endpoints for CLI
    path("api/login/", views.api_login, name="api_login"),
    path("api/signup/", views.api_signup, name="api_signup"),
    path("api/tasks/", views.api_tasks, name="api_tasks"),
    path("api/tasks/add/", views.api_add_task, name="api_add_task"),
    path("api/tasks/<int:task_id>/complete/", views.api_complete_task, name="api_complete_task"),
    path("api/tasks/<int:task_id>/pending/", views.api_pending_task, name="api_pending_task"),
    path("api/tasks/<int:task_id>/edit/", views.api_edit_task, name="api_edit_task"),
    path("api/tasks/<int:task_id>/delete/", views.api_delete_task, name="api_delete_task"),
]
