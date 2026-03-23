from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy import select
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from datetime import datetime, date

# ==========================================
# 1. Database Configuration (SQLite)
# ==========================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./tareas.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# ==========================================
# 2. DATA MODELS (SQLAlchemy)
# ==========================================
class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    contenido = Column(String)
    deadline = Column(Date)
    completada = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ==========================================
# 3. DATA SCHEMAS (Pydantic)
# ==========================================
class TaskCreate(BaseModel):
    titulo: str = Field(min_length=1, description="Título de la tarea")
    contenido: str = Field(min_length=1, description="Contenido de la tarea")
    deadline: date = Field(description="Fecha de vencimiento")

class TaskUpdate(BaseModel):
    completada: bool = Field(description="Estado de completado")

class TaskResponse(BaseModel):
    id: int
    titulo: str
    contenido: str
    deadline: date
    completada: bool
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)

# ===================================================
# 4. LOGIC LAYER (OOP: Encapsulation and Abstraction)
# ===================================================
class TaskManager:
    def __init__(self, db: Session):
        self.db = db
        # Lista de palabras malsonantes.
        self.__palabras_malsonantes = ["idiota", "basura", "maldito", "estúpido"] 

    def _limpiar_contenido(self, texto: str) -> str:
        """Método para limpiar palabras malsonantes"""
        texto_limpio = texto
        for palabra in self.__palabras_malsonantes:
            # Se reemplaza la palabra malsonante por asteriscos
            texto_limpio = texto_limpio.replace(palabra, "***")
        return texto_limpio

    def crear_tarea(self, task: TaskCreate) -> TaskDB:
        # Se usa el método anterior para limpiar el contenido antes de guardarlo
        contenido_seguro = self._limpiar_contenido(task.contenido)
        
        nueva_tarea = TaskDB(
            titulo=task.titulo,
            contenido=contenido_seguro,
            deadline=task.deadline
        )
        self.db.add(nueva_tarea)
        self.db.commit()
        self.db.refresh(nueva_tarea)
        return nueva_tarea

    def obtener_tarea(self, task_id: int) -> TaskDB | None:
        consulta = select(TaskDB).where(TaskDB.id == task_id)
        return self.db.scalars(consulta).first()

    def marcar_como_completada(self, task_id: int) -> TaskDB | None:
        tarea = self.obtener_tarea(task_id)
        if tarea:
            tarea.completada = True
            self.db.commit()
            self.db.refresh(tarea)
        return tarea

    def obtener_tareas_caducadas(self) -> list[TaskDB]:
        fecha_actual = date.today()
        # Se obtienen las tareas donde el deadline sea menor a la fecha actual y no estén completadas
        consulta = select(TaskDB).where(TaskDB.deadline < fecha_actual, TaskDB.completada == False)
        return self.db.scalars(consulta).all()

# ==========================================
# 5. ENDPOINTS RESTful
# ==========================================
app = FastAPI(title="Task Management API", version="1.0.0")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Task Management API"}

@app.post("/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea(task: TaskCreate, db: Session = Depends(get_db)):
    gestor = TaskManager(db)
    return gestor.crear_tarea(task)

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def obtener_tarea(task_id: int, db: Session = Depends(get_db)):
    gestor = TaskManager(db)
    tarea = gestor.obtener_tarea(task_id)
    if not tarea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    return tarea

# Endpoint para completar
@app.put("/tasks/{task_id}/completar", response_model=TaskResponse)
def marcar_completada(task_id: int, db: Session = Depends(get_db)):
    gestor = TaskManager(db)
    tarea_actualizada = gestor.marcar_como_completada(task_id)
    if not tarea_actualizada:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    return tarea_actualizada

# Endpoint para obtener tareas caducadas
@app.get("/tasks/caducadas", response_model=list[TaskResponse])
def obtener_tareas_caducadas(db: Session = Depends(get_db)):
    gestor = TaskManager(db)
    return gestor.obtener_tareas_caducadas()