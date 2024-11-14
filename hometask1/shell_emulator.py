import os
import tarfile
import json
import logging

# Включаем логирование для отладки
logging.basicConfig(level=logging.INFO)

class ShellEmulator:
    def __init__(self, config_file, fs_archive):
        self.config_file = config_file
        self.fs_archive = fs_archive
        self.virtual_fs = self.load_fs()
        self.current_dir = "root"  # Начальная директория - root

    def load_fs(self):
        # Загружаем архив в память
        try:
            with open(self.fs_archive, 'rb') as archive:
                tar = tarfile.open(fileobj=archive, mode='r')
                virtual_fs = {}
                for member in tar.getmembers():
                    path = member.name.strip("/")  # Удаляем ведущие слеши для унификации путей
                    if member.isdir():
                        virtual_fs[path] = "directory"
                    elif member.isfile():
                        virtual_fs[path] = "file"
                tar.close()
                logging.info("Структура virtual_fs:")
                for path, type_ in virtual_fs.items():
                    logging.info(f"{path}: ({type_})")
                return virtual_fs
        except FileNotFoundError:
            logging.error(f"Ошибка: Архив {self.fs_archive} не найден.")
            raise
        except Exception as e:
            logging.error(f"Произошла ошибка при загрузке архива: {e}")
            raise

    def ls(self):
        # Возвращаем список файлов в текущей директории
        return [
            path.split('/')[-1]
            for path in self.virtual_fs
            if path.startswith(self.current_dir) and path != self.current_dir
        ]

    def cd(self, directory):
        # Проверка существования директории
        if directory in self.virtual_fs and self.virtual_fs[directory] == "directory":
            self.current_dir = directory
            logging.info(f"Перешли в директорию: {directory}")
        else:
            logging.error(f"Директория {directory} не найдена.")
            raise FileNotFoundError(f"Директория {directory} не найдена.")

    def tree(self, path="root", level=0):
        # Рекурсивный вывод структуры директорий
        indent = " " * (level * 4)
        print(f"{indent}{path}/")
        for item in self.virtual_fs:
            if item.startswith(path) and item != path:
                print(f"{indent}    {item.split('/')[-1]}")

    def uname(self):
        return "Shell Emulator"

# Функция для запуска эмулятора
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
