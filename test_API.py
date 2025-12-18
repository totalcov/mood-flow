# test_api_working.py
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("=== ТЕСТИРОВАНИЕ API ===")
    
    # 1. Главная страница
    print("\n1. Главная страница:")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 2. Эндпоинт настроений
    print("\n2. Эндпоинт /moods:")
    try:
        response = requests.get(f"{BASE_URL}/moods/")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Найдено записей: {len(data)}")
            for i, mood in enumerate(data[:3], 1):
                print(f"   Запись {i}: {mood.get('mood_type', 'N/A')} ({mood.get('mood_score', 'N/A')}/5)")
        else:
            print(f"   Ответ: {response.text}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # 3. Создание записи
    print("\n3. Создание новой записи:")
    try:
        new_mood = {
            "mood_type": "excited",
            "mood_score": 5,
            "notes": "API работает!"
        }
        response = requests.post(f"{BASE_URL}/moods/", json=new_mood)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 201:
            created = response.json()
            print(f"   ✅ Создана запись ID: {created.get('id')}")
            print(f"   Тип: {created.get('mood_type')}")
            print(f"   Оценка: {created.get('mood_score')}/5")
        else:
            print(f"   Ответ: {response.text}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    print("\n=== ТЕСТ ЗАВЕРШЕН ===")

if __name__ == "__main__":
    test_api()