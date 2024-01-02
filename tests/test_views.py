import os
import django
import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from api.models import Task


# Configuración de entorno y Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


# Fixture para el cliente de la API
@pytest.fixture
def api_client():
    return APIClient()


# Fixture para datos de usuario
@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'password': 'testpassword',
        'email': 'test@example.com',
    }


# Fixture para datos de tarea, depende de user_data
@pytest.fixture
def task_data(user_data):
    return {
        'user': User.objects.create_user(**user_data),
        'task_name': 'Test Task',
        'detail': 'Task details',
        'complete': False,
        'created_at': timezone.now(),
    }


# Fixture para usuario creado a través de la API, depende de api_client y user_data
@pytest.fixture
def user(api_client, user_data):
    response = api_client.post('/signup/', data=user_data)
    return response.data['user']


# Prueba de autenticación mediante token
@pytest.mark.django_db
def test_test_token(api_client, user_data):
    # Crear un usuario y obtener un token
    user = User.objects.create_user(**user_data)
    token = Token.objects.create(user=user)

    # Configurar el cliente de la API con el token
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    # Caso: Éxito al acceder con un token válido
    response = api_client.get('/api/v1/test_token/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == f'Passed for {user.username}!'

    # Caso: Intento de acceso sin proporcionar token
    api_client.credentials()  # Borrar las credenciales
    response = api_client.get('/api/v1/test_token/')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'detail' in response.data
    assert response.data['detail'] == "Authentication credentials were not provided."

    # Caso: Intento de acceso con token inválido
    api_client.credentials(HTTP_AUTHORIZATION='Token invalid_token')
    response = api_client.get('/api/v1/test_token/')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'detail' in response.data
    assert response.data['detail'] == "Invalid token."


# Prueba de inicio de sesión
@pytest.mark.django_db
def test_login(api_client, user_data):
    # Crear un usuario en la base de datos
    User.objects.create_user(**user_data)

    # Intentar iniciar sesión con las credenciales del usuario
    response = api_client.post('/api/v1/login/', data=user_data)

    # Verificar que la respuesta sea exitosa y contenga token y usuario
    assert response.status_code == status.HTTP_200_OK
    assert 'token' in response.data
    assert 'user' in response.data


# Prueba de registro de usuario
@pytest.mark.django_db
def test_signup(api_client, user_data):
    # Intentar registrarse con nuevos datos de usuario
    response = api_client.post('/api/v1/signup/', data=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert 'token' in response.data
    assert 'user' in response.data


# Prueba de obtener la lista de tareas
@pytest.mark.django_db
def test_task_list_get(api_client, task_data):
    # Crear una tarea en la base de datos
    task = Task.objects.create(**task_data)

    # Obtener un token asociado al usuario de la tarea
    token, created = Token.objects.get_or_create(user=task_data['user'])
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    response = api_client.get('/api/v1/tasks/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['task_name'] == task_data['task_name']


# Prueba de creación de tarea
@pytest.mark.django_db
def test_task_list_post(api_client, user_data):
    # Crear un usuario y obtener un token
    user = User.objects.create_user(**user_data)
    token = Token.objects.create(user=user)

    # Configurar el cliente de la API con el token
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    # Datos de la nueva tarea
    task_data = {
        'task_name': 'New Task',
        'detail': 'Task details',
    }

    response = api_client.post('/api/v1/tasks/', data=task_data)

    # Verificar que la respuesta sea exitosa y la tarea se haya creado correctamente
    assert response.status_code == status.HTTP_201_CREATED
    assert Task.objects.count() == 1
    assert Task.objects.first().task_name == task_data['task_name']


# Prueba de obtener detalles de tarea
@pytest.mark.django_db
def test_task_detail_get(api_client, task_data):
    # Crear una tarea en la base de datos
    task = Task.objects.create(**task_data)
    token, created = Token.objects.get_or_create(user=task_data['user'])
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    response = api_client.get(f'/api/v1/task/{task.id}/')

    # Verificar que la respuesta sea exitosa y contenga los detalles correctos de la tarea
    assert response.status_code == status.HTTP_200_OK
    assert response.data['task_name'] == task_data['task_name']


# Prueba de actualizar detalles de tarea (PUT)
@pytest.mark.django_db
def test_task_detail_put(api_client, task_data):
    # Crear una tarea en la base de datos
    task = Task.objects.create(**task_data)
    token, created = Token.objects.get_or_create(user=task_data['user'])

    # Configurar el cliente de la API con el token
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    # Nuevos datos para la tarea
    new_task_data = {
        'task_name': 'Updated Task',
        'detail': 'Updated details',
        'complete': True,
    }
    response = api_client.put(f'/api/v1/task/{task.id}/', data=new_task_data)

    # Verificar que la respuesta sea exitosa y los detalles de la tarea se hayan actualizado correctamente
    assert response.status_code == status.HTTP_200_OK
    assert Task.objects.first().task_name == new_task_data['task_name']


# Prueba de eliminación de tarea
@pytest.mark.django_db
def test_task_detail_delete(api_client, task_data):
    # Crear una tarea en la base de datos
    task = Task.objects.create(**task_data)

    # Obtener un token asociado al usuario de la tarea
    token, created = Token.objects.get_or_create(user=task_data['user'])

    # Configurar el cliente de la API con el token
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    # Caso: Usuario intenta eliminar una tarea que no le pertenece
    another_user = User.objects.create_user(username='anotheruser', password='anotherpassword', email='another@example.com')
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=another_user).key}')
    response = api_client.delete(f'/api/v1/task/{task.id}/')

    # Verificar que la respuesta sea un acceso prohibido (403) y contenga el detalle correspondiente
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'detail' in response.data

    # Caso: Usuario autenticado elimina su propia tarea
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    response = api_client.delete(f'/api/v1/task/{task.id}/')

    # Verificar que la respuesta sea un éxito (204) y que la tarea se haya eliminado correctamente
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Task.objects.count() == 0
