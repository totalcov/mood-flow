# app/backup.py
import json
import sqlite3
from datetime import datetime
import os
from pathlib import Path
import shutil

def get_db_path():
    """Путь к основной БД (в /tmp)"""
    return "/tmp/mood_flow.db"

def get_backup_dir():
    """Директория для бэкапов (НЕ в /tmp)"""
    if os.getenv("RENDER"):
        # На Render: внутри проекта (сохраняется между деплоями)
        return Path("/opt/render/project/src/backups")
    else:
        return Path("./backups")

def get_backup_db_path():
    """Постоянная копия БД (НЕ в /tmp)"""
    backup_dir = get_backup_dir()
    backup_dir.mkdir(exist_ok=True)
    return backup_dir / "mood_flow_latest.db"

def export_to_json():
    """Экспорт в JSON + копия файла БД"""
    db_path = get_db_path()
    backup_dir = get_backup_dir()
    backup_dir.mkdir(exist_ok=True)
    
    if not Path(db_path).exists():
        print("❌ Файл БД не найден для бэкапа")
        return None
    
    try:
        # 1. КОПИРУЕМ ВЕСЬ ФАЙЛ БД (самое важное!)
        backup_db_path = get_backup_db_path()
        shutil.copy2(db_path, backup_db_path)
        print(f"✅ Файл БД скопирован: {backup_db_path}")
        
        # 2. Также делаем JSON бэкап
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM mood_entries ORDER BY created_at")
        entries = [dict(row) for row in cursor.fetchall()]
        
        backup_data = {
            "backup_date": datetime.now().isoformat(),
            "total_entries": len(entries),
            "entries": entries
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = backup_dir / f"mood_backup_{timestamp}.json"
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON бэкап создан: {json_file} ({len(entries)} записей)")
        
        # Очистка старых JSON бэкапов
        cleanup_old_backups(backup_dir)
        
        conn.close()
        return json_file
        
    except Exception as e:
        print(f"❌ Ошибка бэкапа: {e}")
        return None

def import_from_backup():
    """Восстановление из копии БД"""
    db_path = get_db_path()
    backup_db_path = get_backup_db_path()
    
    if not backup_db_path.exists():
        print("ℹ️  Файл бэкапа БД не найден")
        return False
    
    try:
        # КОПИРУЕМ БЭКАП В /tmp
        shutil.copy2(backup_db_path, db_path)
        print(f"✅ БД восстановлена из: {backup_db_path}")
        
        # Проверяем восстановление
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM mood_entries")
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✅ Восстановлено записей: {count}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка восстановления: {e}")
        return False

def cleanup_old_backups(backup_dir, keep_last=3):
    """Удалить старые JSON бэкапы"""
    backups = sorted(backup_dir.glob("mood_backup_*.json"))
    if len(backups) > keep_last:
        for old_backup in backups[:-keep_last]:
            old_backup.unlink()

def check_backup_status():
    """Проверка статуса бэкапов"""
    backup_db_path = get_backup_db_path()
    backup_dir = get_backup_dir()
    
    json_backups = list(backup_dir.glob("mood_backup_*.json"))
    
    return {
        "db_backup_exists": backup_db_path.exists(),
        "db_backup_size": backup_db_path.stat().st_size if backup_db_path.exists() else 0,
        "json_backups_count": len(json_backups),
        "latest_json": json_backups[-1].name if json_backups else None,
        "backup_dir": str(backup_dir)
    }