#!/usr/bin/env python3

import argparse
import hashlib
import json
import os
import stat
import sys

if sys.version_info < (3, 9):
    raise RuntimeError("Python 3.9+ is required")

LARGE_FILE_SIZE_LIMIT = 1_000_000
HASH_ALG = hashlib.sha256

def file_checksum(path):
    with open(path, "rb") as f:
        data = f.read(LARGE_FILE_SIZE_LIMIT)
        hash_temp = HASH_ALG(data)
        if len(data) == LARGE_FILE_SIZE_LIMIT:
            size = os.stat(path).st_size
            hash_temp.update(str(size).encode("utf-8"))
            # Also include a bit of the file ending
            end_size = LARGE_FILE_SIZE_LIMIT // 2
            f.seek(-end_size, 2)
            hash_temp.update(f.read(end_size))
            h = hash_temp.hexdigest()
            return ["large", path, f"{size}:{h}"]
    h = hash_temp.hexdigest()
    return ["file", path, h]

def fast_checksum(path):
    result = []
    paths_queue = [path]
    while paths_queue:
        dirname = paths_queue.pop(0)
        statinfo = os.lstat(dirname)
        if stat.S_ISDIR(statinfo.st_mode):
            for de in os.scandir(dirname):
                if de.is_symlink():
                    target = os.readlink(de.path)
                    result.append(["symlink", de.path, target])
                elif de.is_dir():
                    paths_queue.append(de.path)
                elif de.is_file():
                    result.append(file_checksum(de.path))
                else:
                    raise RuntimeError(f"Unknown type: {de.path}")
        elif stat.S_ISLNK(statinfo.st_mode):
            target = os.readlink(dirname)
            result.append(["symlink", dirname, target])
        else:
            result.append(file_checksum(dirname))
    return result

def cleanup_dot_slash(file_entries):
    for file_entry in file_entries:
        file_entry[1] = file_entry[1].removeprefix("./")

def progress_maybe(it, *, quiet=False):
    if quiet or len(it) < 100:
        yield from it
        return
    try:
        import tqdm
    except ImportError:
        yield from it
        return
    yield from tqdm.tqdm(it)

def run_fast_checksum(path, quiet=False):
    result = []
    if len(path) == 1 and path[0] == "-":
        paths_generator = list(map(str.strip, sys.stdin))
    else:
        paths_generator = path
    for path in progress_maybe(paths_generator, quiet=quiet):
        result += fast_checksum(path)
    if result:
        cleanup_dot_slash(result)
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", default=".", nargs="*")
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()
    result = run_fast_checksum(args.path, args.quiet)
    if result:
        json.dump(result, sys.stdout, indent=2)

if __name__ == "__main__":
    main()
