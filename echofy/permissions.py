from rest_framework.permissions import BasePermission

class IsAdminUserRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == 'admin')

class IsBlogger(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == 'blogger')
    
class IsActivatedUser(BasePermission):
    def has_permission(self, request, view):
        print("🔍 USER:", request.user)
        print("🔍 IS AUTHENTICATED:", request.user.is_authenticated)
        print("🔍 ACTIVATED FIELD:", getattr(request.user, 'activated', 'MISSING'))

        return bool(request.user.is_authenticated and getattr(request.user, 'activated', False))