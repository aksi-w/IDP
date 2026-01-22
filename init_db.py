from backend.database import init_db, SessionLocal
from backend.models import User, UserRole
from backend.auth import hash_password

def create_first_mentor():
    db = SessionLocal()
    
    try:
        existing_mentor = db.query(User).filter(User.role == UserRole.MENTOR).first()
        
        if existing_mentor:
            print("⚠️  Ментор уже существует в базе данных")
            print(f"   Email: {existing_mentor.email}")
            return
        
        print("\n📝 Создание первого ментора...")
        print("-" * 50)
        
        full_name = input("Введите фамилию и имя ментора: ").strip()
        email = input("Введите email: ").strip()
        password = input("Введите пароль: ").strip()
        
        if not full_name or not email or not password:
            print("❌ Все поля обязательны для заполнения!")
            return
        
        mentor = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.MENTOR
        )
        
        db.add(mentor)
        db.commit()
        db.refresh(mentor)
        
        print("\n✅ Ментор успешно создан!")
        print(f"   ID: {mentor.id}")
        print(f"   Фамилия и имя: {mentor.full_name}")
        print(f"   Email: {mentor.email}")
        print("\n🚀 Теперь вы можете войти в систему с этими данными")
        
    except Exception as e:
        print(f"❌ Ошибка при создании ментора: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("  Инициализация базы данных ИПР")
    print("=" * 50)
    
    # Инициализация БД
    print("\n1️⃣  Создание таблиц...")
    init_db()
    print("✅ Таблицы созданы")
    
    # Создание первого ментора
    print("\n2️⃣  Создание первого ментора...")
    create_first_mentor()
    
    print("\n" + "=" * 50)
    print("  Инициализация завершена!")
    print("=" * 50)


