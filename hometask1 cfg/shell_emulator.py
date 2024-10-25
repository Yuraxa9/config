import os
import tarfile
import platform
import json
import logging

logging.basicConfig(level=logging.INFO)


class ShellEmulator:
    def __init__(self, config_path, archive_path):
        logging.info("Initializing Shell Emulator...")

        # Чтение конфигурации
        with open(config_path, 'r') as f:
            config = json.load(f)
            self.archive_name = config.get("fs_archive")

        self.current_dir = "/"
        self.fs = "temp_fs"

        # Создание временной файловой системы
        os.makedirs(self.fs, exist_ok=True)

        # Распаковка архива
        with tarfile.open(archive_path, 'r') as tar:
            tar.extractall(self.fs)

    def ls(self):
        """Список файлов в текущей директории."""
        full_path = os.path.join(self.fs, self.current_dir.strip("/"))
        if os.path.exists(full_path):
            return os.listdir(full_path)
        else:
            raise FileNotFoundError(f"No such directory: {self.current_dir}")

    def cd(self, path):
        """Переход в другую директорию."""
        if path == "..":
            self.current_dir = os.path.dirname(self.current_dir)
        else:
            new_dir = os.path.join(self.current_dir, path).replace("\\", "/")
            full_path = os.path.join(self.fs, new_dir.strip("/"))
            if os.path.exists(full_path):
                self.current_dir = new_dir
            else:
                raise FileNotFoundError(f"No such directory: {new_dir}")
        logging.debug(f"Current directory: {self.current_dir}")

    def mv(self, src, dst):
        """Перемещение файла."""
        src_path = os.path.join(self.fs, self.current_dir.strip("/"), src)
        dst_path = os.path.join(self.fs, self.current_dir.strip("/"), dst)
        if os.path.exists(src_path):
            os.rename(src_path, dst_path)
        else:
            raise FileNotFoundError(f"No such file: {src}")

    def tree(self, directory=None, level=0):
        """Построение структуры файлов."""
        directory = directory or self.current_dir
        full_path = os.path.join(self.fs, directory.strip("/"))
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"No such directory: {directory}")

        tree_output = []
        for item in os.listdir(full_path):
            tree_output.append(f"{'|-- ' * level}{item}")
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                tree_output.extend(self.tree(os.path.join(directory, item), level + 1))
        return tree_output

    def uname(self):
        """Возвращает имя операционной системы."""
        return platform.system()

    def exit(self):
        """Завершение работы эмулятора."""
        logging.info("Exiting Shell Emulator...")
        exit(0)
