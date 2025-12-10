from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mood Flow API",
    description="API для записи ежедневного настроения",
    version="0.1.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в Mood Flow API!",
        "docs": "Документация доступна по адресу /docs"
    }

