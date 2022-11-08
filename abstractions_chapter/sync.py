import hashlib
import os
import shutil
from pathlib import Path

BLOCKSIZE = 65536


def read_paths_and_hashes(root_path: str):
    hashes = {}
    for folder, _, files in os.walk(root_path):
        for fn in files:
            hashes[hash_file(Path(folder) / fn)] = fn
    return hashes


def determine_actions(source_hashes: dict, dest_hashes: dict, source_folder: str, dest_folder: str):
    for sha, filename in source_hashes.items():
        if sha not in dest_hashes:
            sourcepath = Path(source_folder) / filename
            destpath = Path(dest_folder) / filename
            yield 'COPY', sourcepath, destpath

        elif dest_hashes[sha] != filename:
            old_dest_path = Path(dest_folder) / dest_hashes[sha]
            new_dest_path = Path(dest_folder) / filename
            yield 'MOVE', old_dest_path, new_dest_path

    for sha, filename in dest_hashes.items():
        if sha not in source_hashes:
            yield 'DELETE', Path(dest_folder) / filename


def sync(source: str, dest: str):
    # Шаг 1 с императивным ядром: собрать входные данные
    source_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)

    # Шаг 2: вызвать функциональное ядро
    actions = determine_actions(source_hashes, dest_hashes, source, dest)

    # Шаг 3 с императивным ядром: применить операции ввода-вывода данных
    for action, *paths in actions:
        if action == 'COPY':
            shutil.copyfile(*paths)
        if action == 'MOVE':
            shutil.move(*paths)
        if action == 'DELETE':
            os.remove(paths[0])


def hash_file(path: os.path) -> str:
    hasher = hashlib.sha1()
    with path.open('rb') as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()


def synch(source: str, dest: str):
    # Обойти исходную папку и создать словарь путей и хешей
    source_hashes = {}
    for folder, _, files in os.walk(source):
        for fn in files:
            source_hashes[hash_file(Path(folder) / fn)] = fn

    seen = set()  # Отслеживать файлы в целевой папке

    # Обойти целевую папку и получить имена файлов и хеши
    for folder, _, files in os.walk(dest):
        for fn in files:
            dest_path = Path(folder) / fn
            dest_hash = hash_file(dest_path)
            seen.add(dest_hash)

            # Если в целевой папке есть файл, которого нет
            # в источнике, то удалить его
            if dest_hash not in source_hashes:
                print('REMOVE ->', dest_path)
                # dest_path.remove()

            # Если в целевой папке есть файл, который имеет другой
            # путь в источнике, то переместить его в правильный путь
            elif dest_hash in source_hashes and fn != source_hashes[dest_hash]:
                print('MOVE ->', dest_path, 'TO', Path(folder) / source_hashes[dest_hash])
                # shutil.move(dest_path, Path(folder) / source_hashes[dest_hash])

    # Каждый файл, который появляется в источнике, но не в месте назначения, скопировать в целевую папку
    for src_hash, fn in source_hashes.items():
        if src_hash not in seen:
            print('COPY ->', Path(source) / fn, 'TO', Path(dest) / fn)
            # shutil.copy(Path(source) / fn, Path(dest) / fn)
