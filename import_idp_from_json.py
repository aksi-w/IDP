# -*- coding: utf-8 -*-
"""
Скрипт для импорта ИПР из старой системы (JSON файлы)
"""
import json
import sys
from datetime import datetime, timedelta
from backend.database import SessionLocal, init_db
from backend.models import User, IDP, Task, TaskComment, UserRole, TaskStatus, IDPStatus
from backend.auth import generate_access_code

def import_idp_from_json(json_file_path, mentor_email):
    """
    Импортирует ИПР из JSON файла старой системы
    
    Args:
        json_file_path: путь к JSON файлу с данными ИПР
        mentor_email: email ментора в новой системе
    """
    print("=" * 80)
    print(f"📥 ИМПОРТ ИПР ИЗ {json_file_path}")
    print("=" * 80)
    
    # Загружаем JSON
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return
    
    db = SessionLocal()
    try:
        # Находим ментора
        mentor = db.query(User).filter(User.email == mentor_email).first()
        if not mentor:
            print(f"❌ Ментор с email {mentor_email} не найден в системе")
            return
        
        print(f"✅ Ментор найден: {mentor.full_name} ({mentor.email})")
        
        # Данные менти
        profile = data.get('profile', {})
        mentee_name = profile.get('fullName', 'Без имени')
        mentee_position = profile.get('position', None)
        mentee_grade = profile.get('grade', None)
        
        # Пытаемся получить реальный email из JSON
        # Можно передать третий параметр при запуске скрипта
        if len(sys.argv) > 3:
            mentee_email = sys.argv[3]
        else:
            # Генерируем email: имя.фамилия@example.com
            mentee_email = f"{mentee_name.lower().replace(' ', '.')}@example.com"
        
        print(f"\n👤 Создание менти: {mentee_name}")
        print(f"   Email: {mentee_email}")
        print(f"   Должность: {mentee_position}")
        print(f"   Грейд: {mentee_grade}")
        
        # Проверяем существует ли менти
        mentee = db.query(User).filter(User.email == mentee_email).first()
        if mentee:
            print(f"   ⚠️  Менти уже существует (ID: {mentee.id})")
            # Если у существующего менти нет кода - генерируем
            if not mentee.access_code:
                mentee.access_code = generate_access_code()
                db.flush()
                print(f"   ✅ Сгенерирован новый Access Code: {mentee.access_code}")
        else:
            # Создаем менти с access_code
            access_code = generate_access_code()
            mentee = User(
                full_name=mentee_name,
                email=mentee_email,
                role=UserRole.MENTEE,
                access_code=access_code
            )
            db.add(mentee)
            db.flush()
            print(f"   ✅ Менти создан (ID: {mentee.id}, Access Code: {mentee.access_code})")
        
        # Создаем ИПР
        print(f"\n📋 Создание ИПР...")
        idp = IDP(
            mentor_id=mentor.id,
            mentee_id=mentee.id,
            status=IDPStatus.ACTIVE
        )
        db.add(idp)
        db.flush()
        print(f"   ✅ ИПР создан (ID: {idp.id})")
        
        # Импортируем задачи
        print(f"\n📝 Импорт задач...")
        
        tasks_created = 0
        comments_added = 0
        
        # Обрабатываем progress (там актуальные статусы и комментарии)
        progress = data.get('progress', {})
        
        for skill_key, skill_data in progress.items():
            activities = skill_data.get('activities', [])
            skill_name = skill_data.get('name', skill_key)
            
            for activity in activities:
                # Маппинг статусов
                status_map = {
                    'planned': TaskStatus.TODO,
                    'doing': TaskStatus.IN_PROGRESS,
                    'done': TaskStatus.DONE
                }
                
                task_status = status_map.get(activity.get('status', 'planned'), TaskStatus.TODO)
                
                # Рассчитываем deadline
                duration_weeks = activity.get('duration', 4)
                deadline = datetime.now() + timedelta(weeks=duration_weeks)
                
                # Определяем приоритет
                priority_map = {
                    'high': 'high',
                    'medium': 'medium',
                    'low': 'low'
                }
                priority = priority_map.get(activity.get('priority', 'medium'), 'medium')
                
                # Формируем описание
                description_parts = []
                if activity.get('description'):
                    description_parts.append(f"**Описание:**\n{activity['description']}")
                if activity.get('expectedResult'):
                    description_parts.append(f"\n**Ожидаемый результат:**\n{activity['expectedResult']}")
                
                description = "\n\n".join(description_parts) if description_parts else "Нет описания"
                
                # Создаем задачу
                task = Task(
                    idp_id=idp.id,
                    title=activity.get('name', 'Без названия'),
                    description=description,
                    status=task_status,
                    priority=priority,
                    deadline=deadline,
                    linked_skills={
                        'category': 'Импорт из старой системы',
                        'skill': skill_name,
                        'level': activity.get('level'),
                        'related_skills': activity.get('relatedSkills', [])
                    }
                )
                db.add(task)
                db.flush()
                tasks_created += 1
                
                print(f"   ✅ Задача: {activity.get('name', 'Без названия')[:50]}... [{task_status.value}]")
                
                # Добавляем комментарии
                comments = activity.get('comments', [])
                if comments:
                    for comment_data in comments:
                        comment_text = comment_data.get('text', '')
                        if comment_text:
                            comment = TaskComment(
                                task_id=task.id,
                                user_id=mentor.id,
                                comment=comment_text
                            )
                            db.add(comment)
                            comments_added += 1
                            print(f"      💬 Комментарий добавлен")
                
                # Если есть последний комментарий в поле comment
                if activity.get('comment'):
                    comment = TaskComment(
                        task_id=task.id,
                        user_id=mentor.id,
                        comment=activity['comment']
                    )
                    db.add(comment)
                    comments_added += 1
        
        db.commit()
        
        print("\n" + "=" * 80)
        print("📊 СТАТИСТИКА ИМПОРТА")
        print("=" * 80)
        print(f"✅ ИПР создан: ID {idp.id}")
        print(f"✅ Менти: {mentee.full_name}")
        print(f"   Email: {mentee.email}")
        print(f"   🔑 Access Code: {mentee.access_code}")
        print(f"✅ Задач создано: {tasks_created}")
        print(f"✅ Комментариев добавлено: {comments_added}")
        print("=" * 80)
        print("🎉 Импорт завершен успешно!")
        
        # Сохраняем код доступа в файл
        access_codes_file = "access_codes.txt"
        with open(access_codes_file, 'a', encoding='utf-8') as f:
            f.write(f"{mentee.full_name} | {mentee.email} | {mentee.access_code}\n")
        
        print(f"\n💾 Код доступа сохранен в файл: {access_codes_file}")
        
        return {
            'success': True,
            'mentee_name': mentee.full_name,
            'mentee_email': mentee.email,
            'access_code': mentee.access_code,
            'idp_id': idp.id,
            'tasks_count': tasks_created
        }
        
    except Exception as e:
        print(f"\n❌ Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        db.close()


def main():
    if len(sys.argv) < 3:
        print("Использование:")
        print("  python import_idp_from_json.py <путь_к_json> <email_ментора> [email_менти]")
        print("\nПримеры:")
        print("  python import_idp_from_json.py idp_pereguda.json mentor@example.com")
        print("  python import_idp_from_json.py idp_pereguda.json mentor@example.com pereguda@surfstudio.ru")
        return
    
    json_file = sys.argv[1]
    mentor_email = sys.argv[2]
    
    init_db()
    import_idp_from_json(json_file, mentor_email)


if __name__ == "__main__":
    main()
