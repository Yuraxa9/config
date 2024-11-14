import unittest
import os
import shutil
import tarfile
import json
from shell_emulator import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = "temp_fs"
        os.makedirs(cls.temp_dir, exist_ok=True)
        cls.archive_name = "root.tar"
        archive_path = os.path.join(cls.temp_dir, cls.archive_name)

        # Создание тестового архива root.tar
        with tarfile.open(archive_path, 'w') as tar:
            root_dir = os.path.join(cls.temp_dir, "root")
            os.makedirs(root_dir, exist_ok=True)
            with open(os.path.join(root_dir, "text1.txt"), "w") as f:
                f.write("Test file 1")
            with open(os.path.join(root_dir, "text2.txt"), "w") as f:
                f.write("Test file 2")
            with open(os.path.join(root_dir, "text3.txt"), "w") as f:
                f.write("Test file 3")
            tar.add(root_dir, arcname="root")

        config_path = os.path.join(cls.temp_dir, "config.json")
        with open(config_path, 'w') as f:
            json.dump({"fs_archive": cls.archive_name}, f)

        cls.emulator = ShellEmulator(config_path, archive_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_ls(self):
        self.emulator.cd("root")
        output = self.emulator.ls()
        self.assertIn("text1.txt", output)
        self.assertIn("text2.txt", output)
        self.assertIn("text3.txt", output)

    def test_cd(self):
        self.emulator.cd("root")
        self.assertEqual(self.emulator.current_dir, "root")

    def test_mv(self):
        self.emulator.cd("root")
        # Для примера, добавим команду перемещения файлов
        # self.emulator.mv("text1.txt", "newfile.txt")
        # self.assertIn("newfile.txt", self.emulator.ls())
        # self.assertNotIn("text1.txt", self.emulator.ls())

    def test_tree(self):
        output = self.emulator.tree()
        # Проверка содержимого дерева каталогов (тестовый пример)

    def test_uname(self):
        uname_output = self.emulator.uname()
        self.assertEqual(uname_output, "Shell Emulator")

if __name__ == "__main__":
    unittest.main()
