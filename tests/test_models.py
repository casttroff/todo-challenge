import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from api.models import Task
from django.utils import timezone
import os
import django

# Configuración del entorno Django para las pruebas
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Fixture: Configuración de un cliente de API para las pruebas
@pytest.fixture
def api_client():
    return APIClient()

# Fixture: Datos de usuario para las pruebas
@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'password': 'testpassword',
        'email': 'test@example.com',
    }

# Fixture: Datos de tarea para las pruebas, depende de user_data
@pytest.fixture
def task_data(user_data):
    return {
        'user': User.objects.create_user(**user_data),
        'task_name': 'Test Task',
        'detail': 'Task details',
        'complete': False,
        'created_at': timezone.now(),
    }

# Prueba de creación de tarea en la base de datos
@pytest.mark.django_db
def test_create_task(task_data):
    # Crear una tarea utilizando los datos proporcionados por el fixture
    task = Task.objects.create(**task_data)

    # Verificar que la tarea se haya creado correctamente en la base de datos
    assert Task.objects.count() == 1
    assert task.user == task_data['user']
    assert task.task_name == 'Test Task'
    assert task.detail == 'Task details'
    assert not task.complete
    assert task.created_at is not None

# Prueba del método __str__ de la tarea
@pytest.mark.django_db
def test_task_str_method(task_data):
    # Crear una tarea utilizando los datos proporcionados por el fixture
    task = Task.objects.create(**task_data)

    # Verificar que la representación en cadena de la tarea sea la esperada
    assert str(task) == 'Test Task'