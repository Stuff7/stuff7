from django.urls import include, path
from django.contrib.auth import logout as logout_user
from django.shortcuts import redirect

def logout(request):
  logout_user(request)
  return redirect("/")

urlpatterns = [
  path("api/", include("user.urls")),
  path("logout/", logout, name="logout"),
]

handler404 = "user.views.not_found"
