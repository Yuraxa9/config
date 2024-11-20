from emulator import ShellEmulator
import os
import json
import tarfile
import sys
from contextlib import redirect_stdout
from io import StringIO


def suppress_output(func):
    """Декоратор для подавления вывода в stdout."""
    def wrapper(*args, **kwargs):
        with StringIO() as buf, redirect_stdout(buf):
            return func(*args, **kwargs)
    return wrapper


def setup_environment():
    """Создаем временные файлы и конфигурацию для тестов."""
    tar_path = "test_archive.tar"
    with tarfile.open(tar_path, "w") as tar:
        os.mkdir("test_dir")
        with open("test_dir/file1.txt", "w") as f:
            f.write("Hello, World!")
        with open("test_dir/file2.txt", "w") as f:
            f.write("Another file")
        tar.add("test_dir", arcname="test_dir")
        os.remove("test_dir/file1.txt")
        os.remove("test_dir/file2.txt")
        os.rmdir("test_dir")
    config_path = "test_config.json"
    with open(config_path, "w") as f:
        json.dump({"archive_path": tar_path}, f)
    return config_path, tar_path


def cleanup_environment(config_path, tar_path):
    """Удаляем временные файлы и конфигурацию после тестов."""
    os.remove(tar_path)
    os.remove(config_path)


@suppress_output
def test_ls(shell):
    try:
        assert shell.vfs.list_dir("/") == ["test_dir"], "Ошибка в ls для корня"
        shell.vfs.change_dir("/test_dir")
        assert shell.vfs.list_dir(".") == ["file1.txt", "file2.txt"], "Ошибка в ls для test_dir"
        assert shell.vfs.list_dir("/nonexistent") is None, "Ошибка в ls для несуществующей директории"
        return "ls: пройден"
    except AssertionError as e:
        return f"ls: не пройден ({e})"


@suppress_output
def test_cd(shell):
    try:
        assert shell.vfs.change_dir("/test_dir"), "Ошибка перехода в test_dir"
        shell.vfs.change_dir("/test_dir")
        assert shell.vfs.change_dir("/"), "Ошибка перехода в корневую директорию"
        assert not shell.vfs.change_dir("/nonexistent"), "Ошибка перехода в несуществующую директорию"
        return "cd: пройден"
    except AssertionError as e:
        return f"cd: не пройден ({e})"


@suppress_output
def test_mv(shell):
    try:
        shell.vfs.change_dir("/test_dir")
        shell.vfs.move("file1.txt", "/file1_moved.txt")
        assert "file1_moved.txt" in shell.vfs.list_dir("/"), "Ошибка перемещения file1.txt"
        shell.vfs.move("/file1_moved.txt", "/test_dir/file2.txt")
        assert "file2.txt" in shell.vfs.list_dir("/test_dir"), "Ошибка замены файла"
        assert not shell.vfs.move("file2.txt", "/nonexistent/file2.txt"), "Ошибка перемещения в несуществующую директорию"
        return "mv: пройден"
    except AssertionError as e:
        return f"mv: не пройден ({e})"


@suppress_output
def test_exit(shell):
    try:
        shell.running = True
        shell.cmd_exit([])
        assert not shell.running, "Ошибка завершения работы эмулятора"
        return "exit: пройден"
    except AssertionError as e:
        return f"exit: не пройден ({e})"


@suppress_output
def test_tree(shell):
    try:
        shell.vfs.tree()  # Проверяем отсутствие ошибок
        return "tree: пройден"
    except Exception as e:
        return f"tree: не пройден ({e})"


@suppress_output
def test_uname(shell):
    try:
        assert shell.vfs.uname() == "VirtualShell Emulator 1.0", "Ошибка в uname"
        return "uname: пройден"
    except AssertionError as e:
        return f"uname: не пройден ({e})"


if __name__ == "__main__":
    # Настраиваем окружение
    config_path, tar_path = setup_environment()
    shell = ShellEmulator(config_path)

    # Запускаем тесты
    try:
        results = []
        results.append(test_ls(shell))
        results.append(test_cd(shell))
        results.append(test_mv(shell))
        results.append(test_exit(shell))
        results.append(test_tree(shell))
        results.append(test_uname(shell))

        # Выводим результаты
        print("\nРезультаты тестирования:")
        for result in results:
            print(result)

    finally:
        # Удаляем временные файлы
        cleanup_environment(config_path, tar_path)
