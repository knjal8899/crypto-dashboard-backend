from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .serializers import RegisterSerializer, UserSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register a new user",
        description="Create a new user account with username, email, and password",
        request=RegisterSerializer,
        responses={
            201: UserSerializer,
            400: "Bad Request - Invalid data"
        },
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:  # pylint: disable=broad-except
            return Response({"detail": "invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "logged out"}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get current user information",
        description="Retrieve information about the currently authenticated user",
        responses={
            200: UserSerializer,
            401: "Unauthorized - Invalid or missing token"
        },
        tags=["Authentication"]
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)

