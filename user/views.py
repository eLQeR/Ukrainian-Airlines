from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer


@extend_schema_view(
    post=extend_schema(
        summary="Create an account",
        description="User can create his profile, "
                    "password length should be in range (5, 18)",
    )
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


@extend_schema_view(
    put=extend_schema(
        summary="Update the profile",
        description="User can update his personal information, "
                    "password length should be in range (5, 18)",
    ),
    patch=extend_schema(
        summary="Partial update the profile",
        description="User can make partial update of his personal information,"
                    " password length should be in range (5, 18)",

    ),
    get=extend_schema(
        summary="Get his profile",
        description="User can get his personal information",
    ),
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
