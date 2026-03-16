from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .serializers import LoginSerializer, RegisterSerializer, UserListSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .permissions import IsAdminRole
from django.db.models import Q 


@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data.get('email')
        
        # Check if user with email already exists
        if User.objects.filter(email=email).exists():
            return Response({
                "status": "error",
                "message": "A user with this email already exists."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the user
        user = serializer.save()
        return Response({
            "status": "success",
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
                "role": user.role
            }
        }, status=status.HTTP_201_CREATED)
    
    errors = []
    for field, msgs in serializer.errors.items():
        errors.extend(msgs)
    
    return Response({
        "status": "error",
        "message": " ".join(errors)
    }, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "status": "error",
                "message": "User with this email does not exist."
            }, status=status.HTTP_404_NOT_FOUND)
        
        user = authenticate(email=email, password=password)
        if user is None:
            return Response({
                "status": "error",
                "message": "Invalid email or password."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Success - return tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "status": "success",
            "message": "Login successful",
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            },
            "user": {
                "id": user.id,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
                "role": user.role
            }
        }, status=status.HTTP_200_OK)
    
    # Validation errors (like missing email or password)
    errors = []
    for field, msgs in serializer.errors.items():
        errors.extend(msgs)
    
    return Response({
        "status": "error",
        "message": " ".join(errors)
    }, status=status.HTTP_400_BAD_REQUEST)
    
    
#    Get a all users (admin only)
@api_view(['GET'])
@permission_classes([IsAdminRole])
def get_all_users(request):
    users = User.objects.all()
    serializer = UserListSerializer(users, many=True)
    return Response({
        "status": "success",
        "count": users.count(),
        "users": serializer.data
    }, status=status.HTTP_200_OK) 
    
    
    
#Search users by firstname, lastname, or email (admin only)
@api_view(['GET'])
@permission_classes([IsAdminRole])  
def search_users(request):
    """
    Search users by firstname, lastname, or email.
    Pass search term as query parameter: ?q=search_term
    """
    query = request.GET.get('q', '')
    if not query:
        return Response({
            "status": "error",
            "message": "Please provide a search query using ?q=term"
        }, status=status.HTTP_400_BAD_REQUEST)

    users = User.objects.filter(
        Q(firstname__icontains=query) |
        Q(lastname__icontains=query) |
        Q(email__icontains=query)
    )

    serializer = UserListSerializer(users, many=True)
    return Response({
        "status": "success",
        "count": users.count(),
        "users": serializer.data
    }, status=status.HTTP_200_OK)    