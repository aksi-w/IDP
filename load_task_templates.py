import json
import csv
from sqlalchemy import func
from backend.database import SessionLocal, init_db
from backend.models import TaskTemplate

def load_kb_tasks():
    print("📥 Загрузка задач из kb_tasks.json...")
    
    with open('kb_tasks.json', 'r', encoding='utf-8') as f:
        tasks = json.load(f)
    
    db = SessionLocal()
    try:
        count = 0
        for i, task in enumerate(tasks):
            try:
                existing = db.query(TaskTemplate).filter(
                    TaskTemplate.category == task.get('category', ''),
                    TaskTemplate.skill_name == task.get('skillName', ''),
                    TaskTemplate.level == task.get('level'),
                    TaskTemplate.source == 'kb_tasks'
                ).first()
                
                if existing:
                    continue
                
                template = TaskTemplate(
                    category=task.get('category', 'Без категории'),
                    skill_name=task.get('skillName', 'Без названия'),
                    level=task.get('level'),
                    goal=task.get('goal'),
                    description=task.get('description'),
                    criteria=task.get('criteria'),
                    duration_weeks=task.get('durationWeeks'),
                    source='kb_tasks'
                )
                db.add(template)
                count += 1
            except Exception as e:
                print(f"   ⚠ Пропущена задача #{i}: {e}")
                continue
        
        db.commit()
        print(f"✅ Загружено {count} задач из kb_tasks.json")
    except Exception as e:
        print(f"❌ Ошибка при загрузке kb_tasks.json: {e}")
        db.rollback()
    finally:
        db.close()

def load_hardskills():
    print("📥 Загрузка навыков из HardSkills Review QA 4.0.csv...")
    
    db = SessionLocal()
    try:
        count = 0
        with open('HardSkills Review QA 4.0.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            current_category = None
            
            for row in reader:
                group = row['Группа навыков'].strip()
                if group:
                    current_category = group
                    continue
                
                skill = row['Навык'].strip()
                if not skill or not current_category:
                    continue
                
                for level in range(1, 5):
                    level_key = f'Минимальные знания, применение для самых простых задач' if level == 1 else \
                                f'Уверенные знания, применение для повседневных задач' if level == 2 else \
                                f'Глубокие знания, применение знаний, внедрение на проекте, адаптация, обучение' if level == 3 else \
                                f'Очень глубокие знания, применение для задач любой сложности'
                    
                    description = row.get(level_key, '').strip()
                    if not description:
                        continue
                    
                    existing = db.query(TaskTemplate).filter(
                        TaskTemplate.category == current_category,
                        TaskTemplate.skill_name == skill,
                        TaskTemplate.level == level,
                        TaskTemplate.source == 'hardskills'
                    ).first()
                    
                    if existing:
                        continue
                    
                    template = TaskTemplate(
                        category=current_category,
                        skill_name=skill,
                        level=level,
                        goal=f"Достичь уровня {level} по навыку '{skill}'",
                        description=description,
                        criteria="Демонстрация навыка на проекте и подтверждение ментором",
                        duration_weeks=4,
                        source='hardskills'
                    )
                    db.add(template)
                    count += 1
        
        db.commit()
        print(f"✅ Загружено {count} навыков из HardSkills CSV")
    except Exception as e:
        print(f"❌ Ошибка при загрузке HardSkills CSV: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("=" * 80)
    print("🚀 ЗАГРУЗКА ШАБЛОНОВ ЗАДАЧ В БАЗУ ДАННЫХ")
    print("=" * 80)
    
    init_db()
    print("✅ База данных инициализирована")
    
    load_kb_tasks()
    load_hardskills()
    
    db = SessionLocal()
    try:
        total = db.query(TaskTemplate).count()
        by_source = db.query(
            TaskTemplate.source,
            func.count(TaskTemplate.id)
        ).group_by(TaskTemplate.source).all()
        
        print("\n" + "=" * 80)
        print("📊 СТАТИСТИКА")
        print("=" * 80)
        print(f"Всего шаблонов в БД: {total}")
        for source, count in by_source:
            print(f"  - {source}: {count}")
        
        categories = db.query(TaskTemplate.category).distinct().count()
        print(f"Категорий: {categories}")
        print("=" * 80)
        print("✅ Загрузка завершена!")
    finally:
        db.close()

if __name__ == "__main__":
    main()

