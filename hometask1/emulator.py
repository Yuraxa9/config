# emulator.py

import tarfile
import json
import sys
import posixpath
import os

class VirtualFile:
    def __init__(self, name, is_dir=False):
        self.name = name
        self.is_dir = is_dir
        self.children = {}  # Для директорий
        self.content = ""   # Для файлов

class VirtualFileSystem:
    def __init__(self, tar_path):
        self.root = VirtualFile("/", is_dir=True)
        self.current_path = "/"
        self.load_tar(tar_path)
    
    def load_tar(self, tar_path):
        if not tarfile.is_tarfile(tar_path):
            print(f"Tar archive {tar_path} does not exist or is not a valid tar file.")
            sys.exit(1)
        with tarfile.open(tar_path, 'r') as tar:
            for member in tar.getmembers():
                # Пропускаем специальные записи '.', './' и ''
                if member.name in ['.', './', '']:
                    continue
                # Нормализуем путь к POSIX-стилю
                path = '/' + member.name.strip('/')
                parts = path.split('/')

                # Дополнительная проверка: пропускаем добавление дочернего элемента с пустым именем
                if parts[-1] == '':
                    continue

                current = self.root
                for part in parts[1:-1]:
                    if part not in current.children:
                        current.children[part] = VirtualFile(part, is_dir=True)
                    current = current.children[part]
                if member.isdir():
                    current.children[parts[-1]] = VirtualFile(parts[-1], is_dir=True)
                else:
                    vf = VirtualFile(parts[-1], is_dir=False)
                    file_obj = tar.extractfile(member)
                    if file_obj:
                        try:
                            vf.content = file_obj.read().decode('utf-8')
                        except UnicodeDecodeError:
                            vf.content = ""
                    current.children[parts[-1]] = vf
    
    def get_node(self, path):
        if posixpath.isabs(path):
            path = path.lstrip('/')
            current = self.root
        else:
            current = self.root
            if self.current_path != "/":
                parts = self.current_path.strip('/').split('/')
                for part in parts:
                    current = current.children.get(part)
                    if current is None:
                        return None
        if path == "":
            return current
        parts = path.split('/')
        for part in parts:
            if part == "..":
                # Переход в родительскую директорию
                if current == self.root:
                    continue  # Уже в корневой директории
                # Поиск родительской директории путем обхода от корня
                parent = self.root
                parent_path = posixpath.dirname(self.current_path)
                if parent_path != '/':
                    parts_parent = parent_path.strip('/').split('/')
                    for p in parts_parent:
                        if p:
                            parent = parent.children.get(p)
                            if parent is None:
                                break
                current = parent if parent else self.root
            elif part == "." or part == "":
                continue
            else:
                current = current.children.get(part)
                if current is None:
                    return None
        return current
    
    def list_dir(self, path):
        node = self.get_node(path)
        if node and node.is_dir:
            return sorted(node.children.keys())
        else:
            return None
    
    def change_dir(self, path):
        node = self.get_node(path)
        if node and node.is_dir:
            if posixpath.isabs(path):
                self.current_path = posixpath.normpath(path)
            else:
                self.current_path = posixpath.normpath(posixpath.join(self.current_path, path))
            if not self.current_path.startswith('/'):
                self.current_path = '/' + self.current_path
            return True
        else:
            return False
    
    def move(self, src, dest):
        src_node = self.get_node(src)
        if not src_node:
            print(f"mv: cannot stat '{src}': No such file or directory")
            return False

        dest_node = self.get_node(dest)
        if dest_node:
            if dest_node.is_dir:
                # Переместить src в dest директорию
                if src_node.name in dest_node.children:
                    print(f"mv: cannot move '{src}': Destination already has a file named '{src_node.name}'")
                    return False
                dest_node.children[src_node.name] = src_node
                # Удалить из старого местоположения
                src_parent_path, src_name = posixpath.split(src)
                src_parent = self.get_node(src_parent_path)
                if src_parent:
                    del src_parent.children[src_name]
                return True
            else:
                # dest существует и является файлом, заменить его
                dest_parent_path, dest_name = posixpath.split(dest)
                dest_parent = self.get_node(dest_parent_path)
                if not dest_parent or not dest_parent.is_dir:
                    print(f"mv: cannot move '{src}' to '{dest}': No such directory")
                    return False
                dest_parent.children[dest_name] = src_node
                # Удалить из старого местоположения
                src_parent_path, src_name = posixpath.split(src)
                src_parent = self.get_node(src_parent_path)
                if src_parent:
                    del src_parent.children[src_name]
                return True
        else:
            # dest не существует, рассматривать как новое имя
            dest_parent_path, dest_name = posixpath.split(dest)
            dest_parent = self.get_node(dest_parent_path)
            if not dest_parent or not dest_parent.is_dir:
                print(f"mv: cannot move '{src}' to '{dest}': No such directory")
                return False
            if dest_name in dest_parent.children:
                print(f"mv: cannot move '{src}': Destination already has a file named '{dest_name}'")
                return False
            dest_parent.children[dest_name] = src_node
            # Удалить из старого местоположения
            src_parent_path, src_name = posixpath.split(src)
            src_parent = self.get_node(src_parent_path)
            if src_parent:
                del src_parent.children[src_name]
            return True
    
    def tree(self, node=None, prefix=""):
        if node is None:
            node = self.get_node(self.current_path)
            print(self.current_path)
        for idx, child in enumerate(sorted(node.children.values(), key=lambda x: x.name)):
            connector = "├── " if idx < len(node.children) -1 else "└── "
            print(prefix + connector + child.name)
            if child.is_dir:
                extension = "│   " if idx < len(node.children) -1 else "    "
                self.tree(child, prefix + extension)
    
    def uname(self):
        return "VirtualShell Emulator 1.0"

class ShellEmulator:
    def __init__(self, config_path):
        self.load_config(config_path)
        self.vfs = VirtualFileSystem(self.config['archive_path'])
        self.commands = {
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'exit': self.cmd_exit,
            'mv': self.cmd_mv,
            'tree': self.cmd_tree,
            'uname': self.cmd_uname
        }
        self.running = True

    def load_config(self, config_path):
        if not os.path.exists(config_path) or not os.path.isfile(config_path):
            print(f"Configuration file {config_path} does not exist.")
            sys.exit(1)
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def run(self):
        while self.running:
            try:
                cmd_input = input(f"{self.vfs.current_path}$ ").strip()
                if not cmd_input:
                    continue
                parts = cmd_input.split()
                cmd = parts[0]
                args = parts[1:]
                if cmd in self.commands:
                    self.commands[cmd](args)
                else:
                    print(f"{cmd}: command not found")
            except (EOFError, KeyboardInterrupt):
                print()
                break

    def cmd_ls(self, args):
        path = args[0] if args else "."
        listing = self.vfs.list_dir(path)
        if listing is not None:
            print('  '.join(listing))
        else:
            print(f"ls: cannot access '{path}': No such directory")

    def cmd_cd(self, args):
        if not args:
            print("cd: missing operand")
            return
        path = args[0]
        success = self.vfs.change_dir(path)
        if not success:
            print(f"cd: no such file or directory: {path}")

    def cmd_exit(self, args):
        self.running = False

    def cmd_mv(self, args):
        if len(args) != 2:
            print("mv: missing file operand")
            return
        src, dest = args
        self.vfs.move(src, dest)

    def cmd_tree(self, args):
        self.vfs.tree()

    def cmd_uname(self, args):
        print(self.vfs.uname())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python emulator.py <config.json>")
        sys.exit(1)
    config_path = sys.argv[1]
    emulator = ShellEmulator(config_path)
    emulator.run()
