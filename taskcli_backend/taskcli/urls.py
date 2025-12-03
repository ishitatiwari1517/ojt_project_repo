from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),        # ✅ Enables /admin
    path('', include('accounts.urls')),     # App routes
]
