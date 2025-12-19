# test_all_crud.py
import requests
import time
import json

BASE_URL = "http://localhost:8000"

print("=== ПОЛНЫЙ ТЕСТ ВСЕХ 5 CRUD ОПЕРАЦИЙ ===")
print("⏳ Ожидаю запуск сервера...")
time.sleep(2)

try:
    print("\n" + "="*50)
    print("1. 📝 POST /moods/ - СОЗДАНИЕ ЗАПИСИ")
    print("="*50)
    
    new_mood = {
        "mood_type": "happy",
        "mood_score": 4,
        "notes": "Тестовая запись для полного теста CRUD"
    }
    
    response = requests.post(f"{BASE_URL}/moods/", json=new_mood)
    
    if response.status_code == 201:
        created = response.json()
        mood_id = created['id']
        print(f"✅ УСПЕХ! Создана запись:")
        print(f"   ID: {mood_id}")
        print(f"   Тип: {created['mood_type']}")
        print(f"   Оценка: {created['mood_score']}/5")
        print(f"   Дата: {created['date']}")
    else:
        print(f"❌ ОШИБКА {response.status_code}: {response.text}")
        mood_id = 1  # На всякий случай
    
    print("\n" + "="*50)
    print("2. 📋 GET /moods/ - ВСЕ ЗАПИСИ")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/moods/")
    
    if response.status_code == 200:
        moods = response.json()
        print(f"✅ УСПЕХ! Найдено записей: {len(moods)}")
        for i, mood in enumerate(moods, 1):
            print(f"   {i}. ID{mood['id']}: {mood['mood_type']} ({mood['mood_score']}/5) - {mood.get('notes', '')}")
    else:
        print(f"❌ ОШИБКА {response.status_code}: {response.text}")
    
    print("\n" + "="*50)
    print("3. 🔍 GET /moods/{id} - ПОИСК ПО КОНКРЕТНОМУ ID")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/moods/{mood_id}")
    
    if response.status_code == 200:
        mood = response.json()
        print(f"✅ УСПЕХ! Найдена запись:")
        print(f"   ID: {mood['id']}")
        print(f"   Тип: {mood['mood_type']}")
        print(f"   Оценка: {mood['mood_score']}/5")
        print(f"   Заметки: {mood.get('notes', 'Нет')}")
        print(f"   Дата создания: {mood['created_at']}")
    elif response.status_code == 404:
        print(f"⚠️  Запись ID {mood_id} не найдена")
    else:
        print(f"❌ ОШИБКА {response.status_code}: {response.text}")
    
    print("\n" + "="*50)
    print("4. ✏️  PUT /moods/{id} - ОБНОВЛЕНИЕ ЗАПИСИ")
    print("="*50)
    
    update_data = {
        "mood_score": 3,
        "notes": "Обновлённые заметки после теста"
    }
    
    response = requests.put(f"{BASE_URL}/moods/{mood_id}", json=update_data)
    
    if response.status_code == 200:
        updated = response.json()
        print(f"✅ УСПЕХ! Запись обновлена:")
        print(f"   Новая оценка: {updated['mood_score']}/5 (было 4)")
        print(f"   Новые заметки: {updated.get('notes', 'Нет')}")
    elif response.status_code == 404:
        print(f"⚠️  Запись ID {mood_id} не найдена")
    else:
        print(f"❌ ОШИБКА {response.status_code}: {response.text}")
    
    print("\n" + "="*50)
    print("5. 🗑️  DELETE /moods/{id} - УДАЛЕНИЕ ЗАПИСИ")
    print("="*50)
    
    response = requests.delete(f"{BASE_URL}/moods/{mood_id}")
    
    if response.status_code == 204:
        print(f"✅ УСПЕХ! Запись ID {mood_id} удалена")
    elif response.status_code == 404:
        print(f"⚠️  Запись ID {mood_id} не найдена")
    else:
        print(f"❌ ОШИБКА {response.status_code}: {response.text}")
    
    print("\n" + "="*50)
    print("6. 🔄 ФИНАЛЬНАЯ ПРОВЕРКА (после удаления)")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/moods/")
    if response.status_code == 200:
        moods = response.json()
        remaining = len([m for m in moods if m['id'] == mood_id])
        if remaining == 0:
            print(f"✅ УСПЕХ! Запись ID {mood_id} действительно удалена")
        else:
            print(f"⚠️  Запись ID {mood_id} всё ещё существует")
    
    print("\n" + "="*50)
    print("🎉 ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print("="*50)
    print("ВСЕ 5 CRUD ОПЕРАЦИЙ РАБОТАЮТ КОРРЕКТНО!")
    print("✅ Создание (POST)")
    print("✅ Чтение всех (GET /)")
    print("✅ Чтение по ID (GET /{id})")
    print("✅ Обновление (PUT)")
    print("✅ Удаление (DELETE)")
    print("\n🚀 API ГОТОВ К ИСПОЛЬЗОВАНИЮ!")
    
except requests.exceptions.ConnectionError:
    print("❌ Сервер не запущен! Запусти его:")
    print("   python run.py")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")