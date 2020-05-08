from rest_framework import permissions

class IsOwner(permissions.BasePermission):
  def has_object_permission(self, request, view, obj):
    if request.method in permissions.SAFE_METHODS:
      return True
    
    user = request.user
    return user.is_authenticated and user.id == obj.id
