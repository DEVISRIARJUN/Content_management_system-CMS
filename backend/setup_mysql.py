import os
import sys
import pymysql
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

def test_and_setup_mysql():
    print("=" * 60)
    print(" NovaCMS - MySQL Database Diagnostic & Setup")
    print("=" * 60)

    db_host = os.getenv('DB_HOST', '127.0.0.1')
    db_port = int(os.getenv('DB_PORT', '3306'))
    db_user = os.getenv('DB_USER', 'root')
    db_pass = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', 'cms_db')

    print(f"Connecting to MySQL Host : {db_host}:{db_port}")
    print(f"User                     : {db_user}")
    print(f"Target Database          : {db_name}")

    try:
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            port=db_port,
            connect_timeout=5
        )
        print("\n[+] SUCCESS: Connected to MySQL Server!")
        
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f"[+] SUCCESS: Database `{db_name}` verified/created.")
            
            cursor.execute("SHOW DATABASES LIKE %s;", (db_name,))
            res = cursor.fetchone()
            if res:
                print(f"[+] Confirmed database `{db_name}` is ready for Django migrations.")
        
        conn.close()
        print("\n[OK] You are ready to run: python manage.py migrate")
        return True

    except pymysql.err.OperationalError as e:
        print(f"\n[-] Operational Error ({e.args[0]}): {e.args[1]}")
        if e.args[0] == 1045:
            print("[!] Hint: Your MySQL root user has a password set.")
            print("[!] Please open 'backend/.env' and update DB_PASSWORD=your_password")
        return False
    except Exception as e:
        print(f"\n[-] Connection failed: {e}")
        return False

if __name__ == '__main__':
    test_and_setup_mysql()
