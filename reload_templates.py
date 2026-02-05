# -*- coding: utf-8 -*-
"""
Скрипт для ПЕРЕЗАГРУЗКИ шаблонов задач
Очищает старые шаблоны и загружает заново из kb_tasks.json и CSV
"""

from backend.database import SessionLocal, init_db
from backend.models import TaskTemplate
from load_task_templates import load_kb_tasks, load_hardskills
from sqlalchemy import func

def clear_templates():
    """Очистка всех старых шаблонов из БД"""
    print("🗑️  Очистка старых шаблонов...")
    db = SessionLocal()
    try:
        count = db.query(TaskTemplate).delete()
        db.commit()
        print(f"✅ Удалено {count} старых шаблонов")
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("=" * 80)
    print("🔄 ПЕРЕЗАГРУЗКА ШАБЛОНОВ ЗАДАЧ")
    print("=" * 80)
    print()
    
    # Инициализация БД
    init_db()
    print("✅ База данных инициализирована")
    print()
    
    # Очищаем старые шаблоны
    clear_templates()
    print()
    
    # Загружаем заново
    load_kb_tasks()
    print()
    load_hardskills()
    
    # Показываем статистику
    print()
    db = SessionLocal()
    try:
        total = db.query(TaskTemplate).count()
        by_source = db.query(
            TaskTemplate.source,
            func.count(TaskTemplate.id)
        ).group_by(TaskTemplate.source).all()
        
        categories = db.query(TaskTemplate.category).distinct().all()
        
        print("=" * 80)
        print("📊 РЕЗУЛЬТАТ")
        print("=" * 80)
        print(f"Всего шаблонов в БД: {total}")
        print()
        print("По источникам:")
        for source, count in by_source:
            print(f"  - {source}: {count} шаблонов")
        print()
        print(f"Категорий: {len(categories)}")
        print()
        print("Список категорий:")
        for cat in sorted([c[0] for c in categories]):
            count = db.query(TaskTemplate).filter(TaskTemplate.category == cat).count()
            print(f"  - {cat} ({count} задач)")
        
        print("=" * 80)
        print("✅ Перезагрузка завершена успешно!")
        print("=" * 80)
    except Exception as e:
        print(f"❌ Ошибка при выводе статистики: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
