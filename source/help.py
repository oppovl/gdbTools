import gdb
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from helpers.consts import commandsNamePrefix
from helpers.gdbPrinter import printer

class Info(gdb.Command):
    def __init__(self):
        super(Info, self).__init__(f"{commandsNamePrefix}gdbTools-info", gdb.COMMAND_USER)
        self.__commandName = commandsNamePrefix + "gdbTools-info"
        self._info_text = """Designed by 
Email: @gmail.com
Version: 0.1.0"""

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        argc = len(args)
        if argc != 0:
            printer.error("Unexpected arguments")
            return None
        printer.info(self._info_text)

        return None

class Help(gdb.Command):
    def __init__(self):
        super(Help, self).__init__(f"{commandsNamePrefix}gdbTools-help", gdb.COMMAND_USER)
        self.__commandName = commandsNamePrefix + "gdbTools-help"
        self._help_text = """These tools are designed to simplify debugging and memory dump analysis of C++ programs.
It's provide several commands:
Type getters:
\t- gvt             -- a basic command for getting the variable type; displays the type as in GDB;
\t- gbvt            -- attempts to get the type without typedefs or aliases;
\t- gppt            -- attempts to find the actual type from the vtable; if you have a pointer to a base class and want to know what subclass it is, use this command;
\t- gcvt            -- if you have an STL container and just want to know the type of the value in it, use this command;
Stl containers viewer:
\t- icvt            -- is like a very nice printer; helps you view the values of an STL container;
Info:
\t- gdbTools-info   -- shows common info;
\t- gdbTool-help    -- shows this message.
\n\nFor additional information try --help flag with commands. Some commands supports this flag."""

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        argc = len(args)
        if argc != 0:
            printer.error("Unexpected arguments")
            return None

        printer.info(self._help_text)
        return None