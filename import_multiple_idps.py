# -*- coding: utf-8 -*-
"""
Скрипт для пакетного импорта нескольких ИПР
"""
import sys
from import_idp_from_json import import_idp_from_json, init_db

def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python import_multiple_idps.py <файл_со_списком>")
        print("\nФормат файла (каждая строка):")
        print("  путь_к_json,email_ментора,email_менти")
        print("  или")
        print("  путь_к_json,email_ментора")
        print("\nПример файла import_batch.txt:")
        print("  idp_person1.json,mentor1@example.com,person1@surfstudio.ru")
        print("  idp_person2.json,mentor1@example.com,person2@surfstudio.ru")
        print("  idp_person3.json,mentor2@example.com")
        return
    
    batch_file = sys.argv[1]
    
    init_db()
    
    # Очищаем файл с кодами доступа перед импортом
    with open("access_codes.txt", 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("КОДЫ ДОСТУПА ДЛЯ МЕНТИ\n")
        f.write("=" * 80 + "\n\n")
    
    print("=" * 80)
    print("🚀 ПАКЕТНЫЙ ИМПОРТ ИПР")
    print("=" * 80)
    
    results = []
    
    try:
        with open(batch_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total = 0
        success = 0
        failed = 0
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            total += 1
            
            try:
                parts = line.split(',')
                json_file = parts[0].strip()
                mentor_email = parts[1].strip()
                
                # Если указан email менти - передаем его в sys.argv
                if len(parts) > 2:
                    mentee_email = parts[2].strip()
                    import sys as sys_module
                    original_argv = sys_module.argv.copy()
                    sys_module.argv = ['import_idp_from_json.py', json_file, mentor_email, mentee_email]
                    result = import_idp_from_json(json_file, mentor_email)
                    sys_module.argv = original_argv
                else:
                    result = import_idp_from_json(json_file, mentor_email)
                
                if result and result.get('success'):
                    success += 1
                    results.append(result)
                else:
                    failed += 1
                
            except Exception as e:
                print(f"❌ Ошибка обработки строки {i}: {e}")
                failed += 1
        
        print("\n" + "=" * 80)
        print("📊 ИТОГИ ПАКЕТНОГО ИМПОРТА")
        print("=" * 80)
        print(f"✅ Успешно: {success}")
        print(f"❌ Ошибок: {failed}")
        print(f"📝 Всего: {total}")
        print("=" * 80)
        
        # Генерируем красивый отчет
        if results:
            print("\n" + "=" * 80)
            print("🔑 КОДЫ ДОСТУПА ДЛЯ МЕНТИ")
            print("=" * 80)
            for r in results:
                print(f"\n👤 {r['mentee_name']}")
                print(f"   Email: {r['mentee_email']}")
                print(f"   🔑 Код: {r['access_code']}")
                print(f"   ИПР ID: {r['idp_id']}")
                print(f"   Задач: {r['tasks_count']}")
            print("\n" + "=" * 80)
            print(f"💾 Все коды сохранены в файл: access_codes.txt")
            print("=" * 80)
        
    except Exception as e:
        print(f"❌ Ошибка чтения файла списка: {e}")


if __name__ == "__main__":
    main()
