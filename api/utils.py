from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

# Función decoradora para aplicar autenticación y permisos específicos a una vista
def auth_and_perm_classes(view_func):
    return authentication_classes([SessionAuthentication, TokenAuthentication])(
        permission_classes([IsAuthenticated])(view_func)
    )

# Función para encontrar al usuario asociado a un token
def find_user_from_token(token_key):
    try:
        # Intentar obtener el usuario asociado al token
        user = Token.objects.get(key=token_key).user
        return user
    except Token.DoesNotExist:
        # En caso de que el token no exista, devolver una respuesta de error
        return Response({"detail": "Token no válido"}, status=status.HTTP_401_UNAUTHORIZED)
