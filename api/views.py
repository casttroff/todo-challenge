import logging
from datetime import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializer import UserSerializer, TaskSerializer
from .models import Task
from .utils import auth_and_perm_classes, find_user_from_token

# Configuración básica del sistema de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Endpoint para probar la validez del token
@api_view(['GET'])
@auth_and_perm_classes  # Requiere autenticación y permisos específicos (definidos en utils.py)
def test_token(request):
    logger.info(f"GET request to test_token endpoint by user {request.user.username}")
    return Response({"message": f"Passed for {request.user.username}!"})

# Endpoint para iniciar sesión
@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # Autenticar al usuario
    user = authenticate(username=username, password=password)

    if user is not None:
        # Generar o recuperar token para el usuario autenticado
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(instance=user)
        logger.info(f"Successful login attempt for user {username}")
        return Response({"token": token.key, "user": serializer.data})
    else:
        logger.warning(f"Failed login attempt for user {username}")
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# Endpoint para registrarse
@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        # Crear un nuevo usuario
        user = User.objects.create_user(
            username=request.data.get('username'),
            password=request.data.get('password'),
            email=request.data.get('email')
        )
        # Generar token para el nuevo usuario
        token = Token.objects.create(user=user)
        logger.info(f"User {user.username} signed up successfully")
        return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_201_CREATED)

    logger.warning(f"Failed signup attempt")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Endpoint para listar y crear tareas
@api_view(['GET', 'POST'])
@auth_and_perm_classes
def task_list(request):
    if request.method == 'GET':
        created_at = request.query_params.get('created_at', None)
        content_contains = request.query_params.get('content_contains', None)
        tasks = Task.objects.all()

        if created_at:
            try:
                created_at = created_at.strip('"')
                created_at_date = timezone.make_aware(datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ"))
                if created_at_date:
                    # Filtrar tareas por fecha de creación
                    tasks = tasks.filter(created_at__gte=created_at_date)
            except ValueError:
                 return Response({"detail": "Wrong date format."}, status=status.HTTP_404_NOT_FOUND)

        if content_contains:
            # Filtrar tareas por contenido en detalle
            tasks = tasks.filter(detail__icontains=content_contains)

        serializer = TaskSerializer(tasks, many=True)
        logger.info(f"GET request to task_list endpoint by user {request.user.username}")
        return Response(serializer.data)

    elif request.method == 'POST':
        # Crear nueva tarea asociada al usuario autenticado
        user = find_user_from_token(request.auth.key)
        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=user)
            logger.info(f"New task created by user {request.user.username}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f"Failed to create a new task by user {request.user.username}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Endpoint para obtener, actualizar parcialmente, actualizar y eliminar una tarea específica
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@auth_and_perm_classes
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user = find_user_from_token(request.auth.key)

    if request.method == 'GET':
        # Obtener detalles de una tarea específica
        serializer = TaskSerializer(task)
        logger.info(f"GET request to task_detail endpoint by user {request.user.username}")
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Verificar si el usuario que intenta actualizar la tarea es el propietario de la tarea
        if task.user != user:
            logger.warning(f"Unauthorized PUT request to task_detail endpoint by user {user}")
            return Response({"detail": "No tienes permiso para realizar esta acción."}, status=status.HTTP_403_FORBIDDEN)

        # Intentar actualizar la tarea con los datos proporcionados
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            # Guardar los cambios en la tarea
            serializer.save()
            logger.info(f"Task {pk} updated by user {user}")
            return Response(serializer.data)

        # Manejar el caso en que la actualización de la tarea no sea válida
        logger.error(f"Failed to update task {pk} by user {user}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        # Intentar realizar una actualización parcial de la tarea
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            # Guardar los cambios parciales en la tarea
            serializer.save()
            logger.info(f"Task {pk} partially updated by user {request.user.username}")
            return Response(serializer.data)

        # Manejar el caso en que la actualización parcial de la tarea no sea válida
        logger.error(f"Failed to partially update task {pk} by user {request.user.username}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Verificar si el usuario que intenta eliminar la tarea es el propietario de la tarea
        if task.user != user:
            logger.warning(f"Unauthorized DELETE request to task_detail endpoint by user {user}")
            return Response({"detail": "No tienes permiso para realizar esta acción."}, status=status.HTTP_403_FORBIDDEN)

        # Eliminar la tarea
        task.delete()
        logger.info(f"Task {pk} deleted by user {request.user.username}")
        return Response(status=status.HTTP_204_NO_CONTENT)