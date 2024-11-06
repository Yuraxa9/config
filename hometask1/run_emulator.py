import json
import os
from shell_emulator import ShellEmulator

# Замените на ваши реальные пути
config_file = "config.json"
archive_path = "root.tar"  # Или путь к вашему архиву

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
        emulator = ShellEmulator(config_file, os.path.join(os.getcwd(), config['fs_archive'])) #os.getcwd() - текущая директория

    emulator.cd("root") # Переходим в нужную директорию
    files = emulator.ls()
    print("Список файлов:")
    for file in files:
        print(file)

except FileNotFoundError:
    print(f"Ошибка: Файл конфигурации или архив не найден.")
except Exception as e:
    print(f"Произошла ошибка: {e}")