from django.core.cache import cache
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User
from .serializers import LoginSerializer, RegisterSerializer, UserListSerializer
from .permissions import IsAdminRole
from .pagination import UserPagination


# Helper to format serializer errors
def format_serializer_errors(errors):
    messages = []
    for field, msgs in errors.items():
        messages.extend(msgs)
    return " ".join(messages)


# REGISTER USER
@api_view(['POST'])
def register_user(request):

    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": format_serializer_errors(serializer.errors)
        }, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']

    if User.objects.filter(email=email).exists():
        return Response({
            "status": "error",
            "message": "A user with this email already exists."
        }, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()

    # clear cached users
    cache.delete_pattern("users_page_*")

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


# LOGIN USER
@api_view(['POST'])
def login_user(request):

    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": format_serializer_errors(serializer.errors)
        }, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    user = authenticate(email=email, password=password)

    if user is None:

        if not User.objects.filter(email=email).exists():
            return Response({
                "status": "error",
                "message": "User with this email does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "status": "error",
            "message": "Invalid email or password."
        }, status=status.HTTP_400_BAD_REQUEST)

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


# GET ALL USERS (PAGINATED + REDIS CACHE)
@api_view(['GET'])
@permission_classes([IsAdminRole])
def get_all_users(request):

    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    cache_key = f"users_page_{page}_{page_size}"

    cached_data = cache.get(cache_key)

    if cached_data:
        return Response(cached_data)

    users = User.objects.all().order_by('-created_at')

    paginator = UserPagination()
    paginated_users = paginator.paginate_queryset(users, request)

    serializer = UserListSerializer(paginated_users, many=True)

    response = paginator.get_paginated_response({
        "status": "success",
        "users": serializer.data
    })

    cache.set(cache_key, response.data, timeout=900)

    return response


# SEARCH USERS (ADMIN ONLY)
@api_view(['GET'])
@permission_classes([IsAdminRole])
def search_users(request):

    query = request.GET.get('q')

    if not query:
        return Response({
            "status": "error",
            "message": "Please provide a search query using ?q=term"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Normalize query
    query = query.strip().lower()

    # Redis cache key
    cache_key = f"search_users_{query}"

    # Check cache first
    cached_data = cache.get(cache_key)

    if cached_data:
        return Response(cached_data)

    # Query database
    users = User.objects.filter(
        Q(firstname__icontains=query) |
        Q(lastname__icontains=query) |
        Q(email__icontains=query)
    ).order_by('-created_at')

    serializer = UserListSerializer(users, many=True)

    data = {
        "status": "success",
        "count": users.count(),
        "users": serializer.data
    }

    # Store in Redis for 10 minutes
    cache.set(cache_key, data, timeout=600)

    return Response(data, status=status.HTTP_200_OK)