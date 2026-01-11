import json
import sqlite3
from datetime import datetime
import os
from pathlib import Path

def export_to_json():
    """Экспорт всех данных в JSON файл"""
    db_path = get_db_path()
    
    if not Path(db_path).exists():
        print("❌ Файл БД не найден")
        return None
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Получаем все записи
    cursor.execute("SELECT * FROM mood_entries ORDER BY created_at")
    entries = [dict(row) for row in cursor.fetchall()]
    
    # Создаем структуру бэкапа
    backup_data = {
        "backup_date": datetime.now().isoformat(),
        "total_entries": len(entries),
        "entries": entries
    }
    
    # Сохраняем в файл
    backup_dir = get_backup_dir()
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"mood_backup_{timestamp}.json"
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Бэкап создан: {backup_file} ({len(entries)} записей)")
    
    # Удаляем старые бэкапы (оставляем 5 последних)
    cleanup_old_backups(backup_dir)
    
    conn.close()
    return backup_file

def import_from_json(backup_file=None):
    """Импорт данных из JSON файла"""
    db_path = get_db_path()
    
    # Если файл не указан, берем последний бэкап
    if not backup_file:
        backup_dir = get_backup_dir()
        backups = sorted(backup_dir.glob("mood_backup_*.json"))
        if not backups:
            print("❌ Бэкапы не найдены")
            return False
        backup_file = backups[-1]
    
    print(f"🔄 Восстанавливаем из: {backup_file}")
    
    # Читаем бэкап
    with open(backup_file, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    
    # Подключаемся к БД
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Очищаем таблицу (опционально)
    cursor.execute("DELETE FROM mood_entries")
    
    # Восстанавливаем записи
    for entry in backup_data["entries"]:
        cursor.execute("""
            INSERT INTO mood_entries 
            (id, mood_type, mood_score, notes, date, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entry['id'],
            entry['mood_type'],
            entry['mood_score'],
            entry['notes'],
            entry['date'],
            entry['created_at']
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Восстановлено {len(backup_data['entries'])} записей")
    return True

def get_db_path():
    """Получить путь к БД"""
    return "/tmp/mood_flow.db" if os.getenv("RENDER") else "./mood_flow.db"

def get_backup_dir():
    """Получить директорию для бэкапов"""
    if os.getenv("RENDER"):
        # На Render создаем свою директорию
        backup_dir = Path("/opt/render/project/src/backups")
    else:
        backup_dir = Path("./backups")
    return backup_dir

def cleanup_old_backups(backup_dir, keep_last=5):
    """Удалить старые бэкапы"""
    backups = sorted(backup_dir.glob("mood_backup_*.json"))
    if len(backups) > keep_last:
        for old_backup in backups[:-keep_last]:
            old_backup.unlink()
            print(f"🗑️  Удален старый бэкап: {old_backup.name}")