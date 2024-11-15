import os
import tarfile
import logging

class ShellEmulator:
    def __init__(self, fs_archive):
        self.fs_archive = fs_archive
        self.current_dir = "/"
        self.fs = {}
        self.load_fs()

    def load_fs(self):
        try:
            with tarfile.open(self.fs_archive, 'r') as tar:
                tar.extractall("temp_fs")
                for member in tar.getmembers():
                    path = os.path.join("temp_fs", member.name)
                    self.fs[member.name] = path
        except Exception as e:
            logging.error(f"Ошибка при загрузке архива: {e}")
            raise

    def ls(self):
        return list(self.fs.keys())

    def cd(self, directory):
        if directory == "..":
            if self.current_dir != "/":
                self.current_dir = os.path.dirname(self.current_dir)
        elif directory in self.fs:
            self.current_dir = f"/{directory}".rstrip("/")
        else:
            raise FileNotFoundError(f"Директория {directory} не найдена.")

    def mv(self, src, dest):
        if src in self.fs:
            self.fs[dest] = self.fs.pop(src)
        else:
            raise FileNotFoundError(f"Файл {src} не найден.")

    def tree(self):
        return "\n".join(self.fs.keys())
