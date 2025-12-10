import uvicorn
import sys
import os

# Добавляем текущую папку в путь
sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

    