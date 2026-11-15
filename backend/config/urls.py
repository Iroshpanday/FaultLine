from django.contrib import admin
from django.urls import path

from agent.views import ChatView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/stores/<slug:store_slug>/chat", ChatView.as_view(), name="chat"),
]
