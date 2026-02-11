#!/usr/bin/env python3
"""
Главный файл приложения - запускает парсер и GUI
"""
import subprocess
import sys
import threading
import time
import os


def run_parser():
    """Запускает парсер в отдельном потоке"""
    print("📡 Запуск парсера и отправка алертов в Telegram...")
    try:
        result = subprocess.run(
            [sys.executable, 'parser.py'],
            capture_output=False,
            timeout=300
        )
        print("✅ Парсер завершен!")
    except Exception as e:
        print(f"❌ Ошибка при запуске парсера: {e}")


def main():
    """Главная функция - запускает парсер и GUI"""
    print("="*70)
    print("🚗 Запуск приложения мониторинга автомобилей")
    print("="*70)
    
    # Запускаем парсер в отдельном потоке
    parser_thread = threading.Thread(target=run_parser, daemon=True)
    parser_thread.start()
    
    # Даем парсеру время на запуск и отправку первых сообщений
    print("\n⏳ Парсер работает в фоновом режиме...")
    print("   Сообщения отправляются в Telegram...\n")
    
    # Запускаем GUI
    try:
        from app import main as gui_main
        gui_main()
    except Exception as e:
        print(f"❌ Ошибка при запуске GUI: {e}")
        sys.exit(1)
    
    # Ждем завершения парсера
    parser_thread.join(timeout=10)


if __name__ == '__main__':
    # Исправляем кодировку для Windows PowerShell
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    main()
