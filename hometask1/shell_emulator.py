import os
import tarfile
import io
import json
import logging

# Включаем логирование для отладки
logging.basicConfig(level=logging.INFO)

class ShellEmulator:
    def __init__(self, config_file, fs_archive):
        self.config_file = config_file
        self.fs_archive = fs_archive

        # Инициализация виртуальной файловой системы из архива
        self.virtual_fs = self.load_fs()

    def load_fs(self):
        # Загружаем архив в память
        try:
            with open(self.fs_archive, 'rb') as archive:
                # Читаем архив в память
                tar = tarfile.open(fileobj=archive, mode='r')
                virtual_fs = {}
                # Читаем содержимое архива
                for member in tar.getmembers():
                    if member.isdir():
                        virtual_fs[member.name] = "directory"
                    elif member.isfile():
                        virtual_fs[member.name] = "file"
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
        return [path for path in self.virtual_fs.keys() if path != "root"]

    def cd(self, directory):
        # Проверка существования директории
        if directory in self.virtual_fs and self.virtual_fs[directory] == "directory":
            logging.info(f"Перешли в директорию: {directory}")
            return directory
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

# Функция для загрузки конфигурации и запуска эмулятора
def run_emulator():
    # Замените на ваши реальные пути
    config_file = "config.json"
    archive_path = "root.tar"  # Или путь к вашему архиву

    try:
        # Загружаем конфигурацию
        with open(config_file, 'r') as f:
            config = json.load(f)
            # Инициализация эмулятора
            emulator = ShellEmulator(config_file, os.path.join(os.getcwd(), config['fs_archive']))

        emulator.cd("root")  # Переходим в корневую директорию
        files = emulator.ls()  # Получаем список файлов
        print("Список файлов:")
        for file in files:
            print(file)

    except FileNotFoundError:
        print(f"Ошибка: Файл конфигурации или архив не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    run_emulator()
