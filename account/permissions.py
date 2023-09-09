from rest_framework.permissions import IsAuthenticated

class CustomIsAuthenticated(IsAuthenticated):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            self.message = 'Please log in to access this resource.'
            return False
        
        return super().has_permission(request, view)

