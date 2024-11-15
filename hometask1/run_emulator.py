import logging
from shell_emulator import ShellEmulator

# Указываем правильное имя файла архива
try:
    emulator = ShellEmulator("root.tar")
    # Пример использования команды
    print(emulator.ls())
except Exception as e:
    logging.error(f"Ошибка при работе с эмулятором: {e}")
