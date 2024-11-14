import json
import os
from shell_emulator import ShellEmulator

def run_emulator():
    config_file = "config.json"
    archive_path = "root.tar"

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            emulator = ShellEmulator(config_file, os.path.join(os.getcwd(), config['fs_archive']))

        while True:
            command = input("Введите команду: ")
            if command == "ls":
                print("\n".join(emulator.ls()))
            elif command.startswith("cd "):
                directory = command.split(" ", 1)[1]
                emulator.cd(directory)
            elif command == "exit":
                print("Выход из эмулятора.")
                break
            elif command == "tree":
                emulator.tree()
            elif command == "uname":
                print(emulator.uname())
            else:
                print("Неизвестная команда.")

    except FileNotFoundError:
        print(f"Ошибка: Файл конфигурации или архив не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    run_emulator()
