from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import uuid
import os

app = FastAPI()

# --- CORS: пока разрешаем всем (для разработки) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # на проде лучше указать конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Папка для загрузок ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Модели данных ---

class WorkType(BaseModel):
    id: int
    name: str

class ReportOut(BaseModel):
    id: int
    user_id: str
    work_type_id: str
    description: str
    people: str
    volume: str
    machines: str
    photo_url: str

# "База" в памяти (для старта)
WORK_TYPES = [
    WorkType(id=1, name="Земляные работы"),
    WorkType(id=2, name="Бетонирование"),
    WorkType(id=3, name="Монтаж конструкций"),
]

REPORTS: List[ReportOut] = []


# --- Эндпоинты ---

@app.get("/work_types", response_model=List[WorkType])
def get_work_types():
    """
    Возвращает список видов работ.
    Твой фронт делает сюда fetch("/work_types")
    """
    return WORK_TYPES


@app.post("/reports", response_model=ReportOut)
async def create_report(
    user_id: str = Form(...),
    work_type_id: str = Form(...),
    description: str = Form(""),
    people: str = Form(""),
    volume: str = Form(""),
    machines: str = Form(""),
    photo: UploadFile = File(...),
):
    """
    Принимает форму с отчётом и одним фото.
    Полностью совпадает с тем, что ты собираешь в FormData на фронте.
    """

    # 1. сохраняем файл на диск
    ext = os.path.splitext(photo.filename or "")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await photo.read())

    photo_url = f"/uploads/{filename}"

    # 2. сохраняем запись в "базу"
    new_id = len(REPORTS) + 1
    report = ReportOut(
        id=new_id,
        user_id=user_id,
        work_type_id=work_type_id,
        description=description,
        people=people,
        volume=volume,
        machines=machines,
        photo_url=photo_url,
    )
    REPORTS.append(report)

    return report


# --- отдаём загруженные файлы как статику ---
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
