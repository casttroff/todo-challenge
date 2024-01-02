## Instrucciones de Uso

1. **Instalación de Docker:**
   - Asegúrate de tener Docker instalado.

2. **Ejecución de la Aplicación:**
   - Abre una terminal de linea de comandos y en el directorio raíz del proyecto ejecuta el siguiente comando:
     ```bash
     docker-compose up
     ```
   - Abre una nueva terminal de linea de comandos y ejecuta el siguiente comando:
     ```bash
     docker exec -it container-djangoapi python manage.py migrate
     ```

3. **Ejecución de Pruebas:**
   - Ejecuta las pruebas utilizando el siguiente comando:
     ```bash
     docker exec -it container-djangoapi pytest
     ```
   - Las pruebas incluyen casos para la creación de usuarios, inicio de sesión, generación y validación de tokens, así como operaciones CRUD en las tareas.
   - Consulta los archivos `tests/test_views.py` y `tests/test_models.py` para obtener detalles adicionales sobre las pruebas implementadas.

4. **Endpoints Habilitados:**

   - [POST] [http://127.0.0.1:8000/api/v1/signup/](http://127.0.0.1:8000/api/v1/signup/)
   - [POST] [http://127.0.0.1:8000/api/v1/login/](http://127.0.0.1:8000/api/v1/login/)
   - [GET] [http://127.0.0.1:8000/api/v1/test_token/](http://127.0.0.1:8000/api/v1/test_token/)
   - [GET, POST] [http://127.0.0.1:8000/api/v1/tasks](http://127.0.0.1:8000/api/v1/tasks)
   - [GET] [http://127.0.0.1:8000/api/v1/tasks/?created_at={date}](http://127.0.0.1:8000/api/v1/tasks/?created_at={date})
   - [GET] [http://127.0.0.1:8000/api/v1/tasks/?content_contains={content_in_detail}](http://127.0.0.1:8000/api/v1/tasks/?content_contains={content_in_detail})
   - [GET, PUT, PATCH, DELETE] [http://127.0.0.1:8000/api/v1/task/{id}/](http://127.0.0.1:8000/api/v1/task/{id}/)

5. **Pasos para Realizar un Circuito de CRUD con Autenticación:**
   -   Realizar signup.
   -   Realizar login para obtener token.
   -   Probar el token generado haciendo una petición GET a /test_token agregando en 'Authorization' el token del usuario.
   -   Ya puedes realizar todas las operaciones CRUD con este token.

6. **Más ejemplos de Pruebas en `tests.rest`:**

   - Puedes utilizar los siguientes ejemplos para probar los endpoints. Copia y pega cada ejemplo en tu herramienta de pruebas, como Postman o curl.

   ```http
   POST http://127.0.0.1:8000/api/v1/signup/
   Content-Type: application/json

   {"username": "test_user", "password": "test_password", "email": "test@gmail.com"}


   POST http://127.0.0.1:8000/api/v1/login/
   Content-Type: application/json

   {"username": "test_user", "password": "test_password"}


   POST http://127.0.0.1:8000/api/v1/tasks/
   Content-Type: application/json
   Authorization: Token b294fbd5ecc0d5311907b0648638c38300f58af9

   {"task_name": "Tarea matutina", "detail": "Tarea 1", "complete": 0}


   GET http://127.0.0.1:8000/api/v1/tasks/
   Content-Type: application/json
   Authorization: Token ...


   GET http://127.0.0.1:8000/api/v1/task/1/
   Content-Type: application/json
   Authorization: Token ...

5. **Consideraciones:**
   - Cada usuario tiene acceso a ver todas las tareas pero solo puede modificar o eliminar su propia tarea.