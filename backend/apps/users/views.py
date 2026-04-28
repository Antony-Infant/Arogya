from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer, UpdateLocationSerializer, MedicalProfileSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """Register a new user account."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'message': 'Account created successfully. Please login.'
        }, status=status.HTTP_201_CREATED)

class ProfileView(generics.RetrieveUpdateAPIView):
    """Get or update user profile."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UpdateLocationView(APIView):
    """Update user's current location for nearby hospital search."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UpdateLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.location_lat = serializer.validated_data['lat']
        request.user.location_lng = serializer.validated_data['lng']
        request.user.save(update_fields=['location_lat', 'location_lng'])
        return Response({'status': 'Location updated successfully'})

class MedicalProfileView(generics.UpdateAPIView):
    """Update medical profile (conditions, allergies, medications)."""
    serializer_class = MedicalProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
