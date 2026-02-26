###
### AUTHENTICATION
###
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.serializers import CustomTokenObtainPairSerializer, UserSerializer, RegistrationSerializer
from apps.users.utils import set_auth_cookies


@extend_schema(tags=['Authentication'])
class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        refresh = CustomTokenObtainPairSerializer.get_token(user)
        access_token = refresh.access_token

        resp = Response(
            UserSerializer(user, context={"request": request}).data,
            status=201
        )

        set_auth_cookies(resp, str(access_token), str(refresh))

        return resp


@extend_schema(tags=['Authentication'])
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        tokens = serializer.validated_data
        access_token = tokens.get('access')
        refresh_token = tokens.get('refresh')

        user_data = UserSerializer(user).data

        response = Response({
            "message": "success",
            "user": user_data,
        })

        set_auth_cookies(response, access_token, refresh_token)

        return response


@extend_schema(tags=['Authentication'])
class CustomTokenRefreshView(APIView):
    serializer_class = TokenRefreshSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get('refresh-token')
        if refresh:
            try:
                data = request.data.copy()
                data['refresh'] = refresh

                serializer = self.serializer_class(data=data)
                serializer.is_valid(raise_exception=True)
            except (TokenError, InvalidToken):
                return Response(
                    {"message": "Invalid refresh token."},
                    status=400
                )

            new_access = serializer.validated_data.get('access')
            new_refresh = serializer.validated_data.get('refresh')

            response = Response(
                {"message": "Refreshed successfully."},
                status=200
            )

            set_auth_cookies(response, new_access, new_refresh)
            return response

        else:
            return Response(
                {"message": "Refresh token is missing in cookies."},
                status=401
            )


@extend_schema(tags=['Authentication'])
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get('refresh-token')
        if refresh:
            try:
                refresh_token = RefreshToken(refresh)
                refresh_token.blacklist()
            except (TokenError, InvalidToken):
                pass

        response = Response({"message": "Successfully logged out."}, status=200)

        response.delete_cookie('access-token')
        response.delete_cookie('refresh-token')

        return response
