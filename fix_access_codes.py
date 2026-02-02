# -*- coding: utf-8 -*-
"""
Скрипт для генерации access_code для существующих менти без кода
"""
from backend.database import SessionLocal, init_db
from backend.models import User, UserRole
from backend.auth import generate_access_code

def fix_access_codes():
    print("🔧 Исправление access_code для менти...")
    
    db = SessionLocal()
    try:
        # Находим всех менти без access_code
        mentees = db.query(User).filter(
            User.role == UserRole.MENTEE,
            User.access_code == None
        ).all()
        
        if not mentees:
            print("✅ Все менти уже имеют access_code")
            return
        
        print(f"Найдено {len(mentees)} менти без кода\n")
        
        for mentee in mentees:
            mentee.access_code = generate_access_code()
            print(f"✅ {mentee.full_name} | {mentee.email} | 🔑 {mentee.access_code}")
        
        db.commit()
        
        print(f"\n✅ Обновлено {len(mentees)} менти")
        
        # Сохраняем коды в файл
        with open("access_codes.txt", 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("КОДЫ ДОСТУПА ДЛЯ МЕНТИ\n")
            f.write("=" * 80 + "\n\n")
            
            all_mentees = db.query(User).filter(User.role == UserRole.MENTEE).all()
            for m in all_mentees:
                f.write(f"{m.full_name} | {m.email} | {m.access_code}\n")
        
        print(f"💾 Коды сохранены в файл: access_codes.txt")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    fix_access_codes()
