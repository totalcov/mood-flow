from app.database import SessionLocal, engine
from app.models.mood import MoodEntry

# Создаем сессию БД
db = SessionLocal()

try:
    # 1. Проверяем подключение
    print("1. Проверка подключения к БД...")
    connection = engine.connect()
    print("✅ Подключение успешно!")
    connection.close()
    
    # 2. Пробуем получить все записи (пока пусто)
    print("\n2. Получение всех записей...")
    entries = db.query(MoodEntry).all()
    print(f"   Всего записей в базе: {len(entries)}")
    
    # 3. Создаем тестовую запись
    print("\n3. Создание тестовой записи...")
    test_entry = MoodEntry(
        score=5, 
        note="Отличный день! База данных работает!"
    )
    db.add(test_entry)
    db.commit()
    db.refresh(test_entry)
    
    print(f"   ✅ Создана запись:")
    print(f"      ID: {test_entry.id}")
    print(f"      Оценка: {test_entry.score}")
    print(f"      Заметка: {test_entry.note}")
    print(f"      Дата: {test_entry.date}")
    
    # 4. Читаем все записи снова
    print("\n4. Проверка чтения записей...")
    entries = db.query(MoodEntry).all()
    print(f"   Теперь записей: {len(entries)}")
    
    for entry in entries:
        print(f"   - ID:{entry.id}, Оценка:{entry.score}, Заметка: {entry.note[:20]}...")
    
    print("\n🎉 Все тесты прошли успешно! База данных работает корректно.")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    db.rollback()
    
finally:
    db.close()