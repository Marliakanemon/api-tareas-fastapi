import requests
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"

def imprimir_resultado(nombre_test, status_real, status_esperado, exito_adicional=True):
    if status_real == status_esperado and exito_adicional:
        print(f"✅ {nombre_test} | Status: {status_real}")
    else:
        print(f"❌ {nombre_test} | Status: {status_real} (Esperado: {status_esperado})")

def test_crear_tarea():
    # Lógica de POO enviando la palabra malsonante "basura"
    deadline_futuro = (date.today() + timedelta(days=5)).isoformat()
    payload = {
        "titulo": "Evaluación final Módulo", 
        "contenido": "Tengo que entregar esto, este script no se si es basura o si sirve.", 
        "deadline": deadline_futuro
    }
    res = requests.post(f"{BASE_URL}/tasks/", json=payload)
    
    # Se valida que el status sea 201 y que la palabra se haya censurado con ***
    json_res = res.json()
    censurado = "***" in json_res.get("contenido", "")
    imprimir_resultado("Crear Tarea (y probar censura POO)", res.status_code, 201, censurado)
    return json_res.get("id")

def test_obtener_tarea(task_id):
    res = requests.get(f"{BASE_URL}/tasks/{task_id}")
    imprimir_resultado(f"Obtener Tarea ID {task_id}", res.status_code, 200)

def test_marcar_completada(task_id):
    # La URL ya tiene la acción completar
    res = requests.put(f"{BASE_URL}/tasks/{task_id}/completar")
    json_res = res.json()
    completada = json_res.get("completada") == True
    imprimir_resultado("Marcar Tarea como Completada", res.status_code, 200, completada)

def test_crear_y_obtener_tareas_caducadas():
    # Se crea una tarea con fecha en el pasado
    deadline_pasado = (date.today() - timedelta(days=2)).isoformat()
    payload = {
        "titulo": "Tarea olvidada", 
        "contenido": "Esta tarea ya caducó", 
        "deadline": deadline_pasado
    }
    requests.post(f"{BASE_URL}/tasks/", json=payload)
    
    res = requests.get(f"{BASE_URL}/tasks/caducadas")
    es_lista = isinstance(res.json(), list)
    imprimir_resultado("Obtener Tareas Caducadas", res.status_code, 200, es_lista)

def test_datos_incorrectos():
    """Test con datos incorrectos para devolver 422"""
    payload_malo = {
        "titulo": "Test incorrecto", 
        "contenido": "Fecha NO válida", 
        "deadline": "no-soy-una-fecha"  # Pydantic rechazará esto
    }
    res = requests.post(f"{BASE_URL}/tasks/", json=payload_malo)
    imprimir_resultado("Manejo de Errores Pydantic (Datos Incorrectos)", res.status_code, 422)

if __name__ == "__main__":
    print("Ejecutando tests...\n")
    try:
        requests.get(BASE_URL)
        
        id_creada = test_crear_tarea()
        if id_creada:
            test_obtener_tarea(id_creada)
            test_marcar_completada(id_creada)
            
        test_crear_y_obtener_tareas_caducadas()
        test_datos_incorrectos()
        
        print("\n Tests completados")
    except requests.exceptions.ConnectionError:
        print("ERROR: El servidor no está corriendo. Ejecutar 'uvicorn main:app --reload'")