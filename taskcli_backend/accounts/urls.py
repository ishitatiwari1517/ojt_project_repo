from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_page, name="login"),
    path("login/", views.do_login, name="do_login"),
    path("register/", views.do_signup, name="do_signup"),
    path("dashboard/", views.dashboard_page, name="dashboard"),
    path("add-task/", views.add_task, name="add_task"),
    path("complete-task/<int:task_id>/", views.complete_task, name="complete_task"),
    path("delete-task/<int:task_id>/", views.delete_task, name="delete_task"),
    path("logout/", views.do_logout, name="logout"),
]
