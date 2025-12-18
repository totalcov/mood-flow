from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.moods import router

tags_metadata = [
    {
        "name": "moods",
        "description": "Операции с записями настроения",
    }
]

app = FastAPI(
    title="Mood Flow API",
    description="API для отслеживания настроения",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/", tags=["default"])
def read_root():
    return {"message": "Mood Flow API работает!"}

@app.get("/health", tags=["default"])
def health_check():
    return {"status": "healthy"}