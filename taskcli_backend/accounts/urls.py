"""
URL Configuration for TaskCLI Accounts App
===========================================
Defines all URL routes for authentication and task operations.

Author: TaskCLI Team
"""

from django.urls import path
from . import views

# URL patterns for the accounts app
urlpatterns = [
    # ==========================================================================
    # AUTHENTICATION ROUTES
    # ==========================================================================
    path("", views.login_page, name="login"),           # Home/Login page
    path("login/", views.do_login, name="do_login"),    # Login form handler
    path("register/", views.do_signup, name="do_signup"),  # Registration handler
    path("logout/", views.do_logout, name="logout"),    # Logout handler
    
    # ==========================================================================
    # DASHBOARD
    # ==========================================================================
    path("dashboard/", views.dashboard_page, name="dashboard"),  # Main dashboard
    
    # ==========================================================================
    # TASK CRUD OPERATIONS
    # ==========================================================================
    path("add-task/", views.add_task, name="add_task"),  # Create new task
    path("edit-task/<int:task_id>/", views.edit_task, name="edit_task"),  # Edit task
    path("complete-task/<int:task_id>/", views.complete_task, name="complete_task"),  # Mark complete
    path("pending-task/<int:task_id>/", views.pending_task, name="pending_task"),  # Mark pending
    path("delete-task/<int:task_id>/", views.delete_task, name="delete_task"),  # Delete task
]
