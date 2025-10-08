import gdb
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from helpers.consts import commandsNamePrefix
from helpers.gdbPrinter import printer


class CacheStorage:
    def __init__():
        pass


    def store(self):
        pass


    def get(self):
        pass


    def delete(self):
        pass


    def update(self):
        pass


    def clear(self):
        pass

    def list(self):
        pass


cache = CacheStorage()

class CacheList(gdb.Command):
    def __init__(self):
        super(CacheList, self).__init__(f"{commandsNamePrefix}cache-list", gdb.COMMAND_USER)
        self.__commandName = commandsNamePrefix + "cache"

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        argc = len(args)
        if argc != 0:
            printer.error("Unexpected arguments")
            return None

        printer.data(cache.list())

        return None