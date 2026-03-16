from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User


@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
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
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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