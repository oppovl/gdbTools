import gdb
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from helpers.consts import commandsNamePrefix
from helpers.gdbPrinter import printer


class CacheStorage:
    def __init__(self):
        self._storage = dict()
        self._storage_keys = list()


    def store(self, key: str, value: dict) -> None:
        self._storage[key] = value
        self._storage_keys.append(key)


    def get(self, key: str) -> dict:
        if key in self._storage_keys:
            return self._storage.get(key)
        else:
            printer.error(f"Key {key} not found in storage")
            return {}


    def delete(self, key: str) -> None:
        if key in self._storage_keys:
            self._storage.pop(key)
            self._storage_keys.remove(key)


    def update(self, key: str, value: dict) -> None:
        if key in self._storage_keys:
            self._storage[key] = value
        else:
            self.store(key, value)


    def clear(self) -> None:
        self._storage.clear()
        self._storage_keys.clear()

    def list(self) -> None:
        if not len(self._storage_keys):
            printer.data(f"Storage is empty")
        else:
            printer.data(f"Storage keys: {self._storage_keys}")


cache = CacheStorage()

class CacheList(gdb.Command):
    def __init__(self):
        super(CacheList, self).__init__(f"{commandsNamePrefix}cache-list", gdb.COMMAND_USER)
        self.__commandName = commandsNamePrefix + "cache-list"

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        argc = len(args)
        if argc != 0:
            printer.error("Unexpected arguments")
            return None

        cache.list()

        return None