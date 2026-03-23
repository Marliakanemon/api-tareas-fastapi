# Task Management API

API RESTful para la gestión de tareas desarrollada con FastAPI. 

## Tecnologías Utilizadas
* **Framework Web:** FastAPI
* **Base de Datos:** SQLite con SQLAlchemy (ORM)
* **Validación de Datos:** Pydantic 
* **Testing:** Librería `requests`

## Instalación y Configuración

1. Crear y activar el entorno virtual

**En Linux:**
python -m venv venv
source venv/bin/activate

2. Instalar dependencias

pip install -r requirements.txt

3. Ejecutar la aplicación

uvicorn main:app --reload

La API estará disponible en http://localhost:8000


## Endpoints Implementados 

A continuación, una breve descripción de los endpoints implementados:

GET /

Descripción: Endpoint raíz que devuelve la información básica y el estado de la API.

POST /tasks/

Descripción: Permite crear una nueva tarea.

Lógica POO: Utiliza la clase TaskManager para aplicar encapsulamiento. Antes de guardar en la base de datos, un método privado limpia el contenido de la tarea censurando palabras prohibidas (ej. "basura", "maldito").

GET /tasks/{task_id}

Descripción: Obtiene el detalle de una tarea específica mediante su ID. Devuelve un error 404 Not Found si la tarea no existe.

PUT /tasks/{task_id}/completar

Descripción: Marca una tarea existente como completada.

Lógica RESTful: No requiere enviar un Payload (Body) en la petición, la propia URL define semánticamente la acción a realizar sobre el recurso.

GET /tasks/caducadas

Descripción: Devuelve una lista de todas las tareas cuya fecha de vencimiento (deadline) es anterior a la fecha actual y que aún no han sido completadas.

## Ejecutar Tests 

La actividad incluye un script de pruebas que valida el correcto funcionamiento de todos los verbos HTTP y el manejo de errores (códigos 200, 201, 404 y 422).

Asegurarse de que FastAPI esté corriendo en una terminal. Luego, en otra terminal ejecutar:

python test_api.py

## Documentación Interactiva

Una vez ejecutando la aplicación, puedes acceder a:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
