# -*- coding: utf-8 -*-

from backend.database import SessionLocal, init_db
from backend.models import TaskTemplate
from load_task_templates import load_kb_tasks, load_hardskills

def clear_templates():
    print("🗑Очистка старых шаблонов...")
    db = SessionLocal()
    try:
        count = db.query(TaskTemplate).delete()
        db.commit()
        print(f"Удалено {count} старых шаблонов")
    except Exception as e:
        print(f"Ошибка при очистке: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("=" * 80)
    print("ПЕРЕЗАГРУЗКА ШАБЛОНОВ ЗАДАЧ")
    print("=" * 80)
    
    init_db()
    print("База данных инициализирована")
    
    # Очищаем старые шаблоны
    clear_templates()
    
    # Загружаем заново с нормализацией
    load_kb_tasks()
    load_hardskills()
    
    # Показываем статистику
    db = SessionLocal()
    try:
        total = db.query(TaskTemplate).count()
        categories = db.query(TaskTemplate.category).distinct().all()
        
        print("\n" + "=" * 80)
        print("РЕЗУЛЬТАТ")
        print("=" * 80)
        print(f"Всего шаблонов: {total}")
        print(f"Категорий: {len(categories)}")
        print("\nКатегории:")
        for cat in sorted([c[0] for c in categories]):
            count = db.query(TaskTemplate).filter(TaskTemplate.category == cat).count()
            print(f"  - {cat} ({count} задач)")
        print("=" * 80)
        print("Перезагрузка завершена!")
    finally:
        db.close()

if __name__ == "__main__":
    main()
