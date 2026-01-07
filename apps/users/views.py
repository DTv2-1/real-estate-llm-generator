"""
Views for Users API.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import CustomUser
from .serializers import RegisterSerializer, UserProfileSerializer


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    
    POST /auth/register
    {
        "username": "john",
        "email": "john@example.com",
        "password": "securepass123",
        "password2": "securepass123",
        "tenant": "tenant-uuid",
        "role": "buyer"
    }
    """
    
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        """Create user and return success message."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'status': 'success',
            'message': 'User registered successfully',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update user profile.
    
    GET /auth/profile
    PATCH /auth/profile
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        """Return current user."""
        return self.request.user
