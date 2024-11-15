import unittest
from shell_emulator import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        # Указываем правильное имя файла архива
        self.emulator = ShellEmulator("root.tar")

    def test_ls(self):
        self.emulator.cd("root")
        files = self.emulator.ls()
        # Проверим наличие файлов, которые находятся в архиве
        self.assertIn("root/text1.txt", files)
        self.assertIn("root/text2.txt", files)
        self.assertIn("root/text3.txt", files)

    def test_cd(self):
        # Перемещаемся в директорию root и проверяем
        self.emulator.cd("root")
        self.assertEqual(self.emulator.current_dir, "/root")

    def test_mv(self):
        # Переименуем файл root/text1.txt в root/text1_renamed.txt
        self.emulator.cd("root")
        self.emulator.mv("root/text1.txt", "root/text1_renamed.txt")
        files = self.emulator.ls()
        # Проверяем, что файл переименован
        self.assertIn("root/text1_renamed.txt", files)
        self.assertNotIn("root/text1.txt", files)

    def test_tree(self):
        # Проверим структуру файловой системы
        structure = self.emulator.tree()
        self.assertIn("root", structure)
        self.assertIn("root/text1.txt", structure)
        self.assertIn("root/text2.txt", structure)
        self.assertIn("root/text3.txt", structure)

if __name__ == '__main__':
    unittest.main()
