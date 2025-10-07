import gdb
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir + "/helpers")

from helpers import commonTools, gdbPrinter, consts

commandsNamePrefix = consts.commandsNamePrefix

from helpers.gdbPrinter import printer

# !!!!! GET VARIABLE TYPE !!!!!
# Retruns type like in gdb (with astericses and aliases)
# Saves result in $result by default
class GetVarType(gdb.Command):
    def __init__(self):
        super(GetVarType, self).__init__(f"{commandsNamePrefix}gvt", gdb.COMMAND_USER)
        self.__commandName = commandsNamePrefix + "gvt"

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        argc = len(args)
        if argc != 1 or (argc == 1 and args[0] == "help"):
            self.__printUsage()
            return None
        
        try:
            var_type = self._getType(args[0])
            maybe_string = commonTools.recognize_string(var_type)
            if maybe_string == str(var_type):
                printer.data(var_type)
            else:
                printer.data(maybe_string)
        except Exception as e:
            printer.error(f"Error occured: {e}")

    def _getType(self, identificator: str) -> gdb.Type:

        if commonTools.is_address(identificator):
            printer.warning("It seems like an address. Cast to a pointer to some type and try again")
            return None
        
        gdbObj = gdb.parse_and_eval(identificator)
        return commonTools.get_variable_type(gdbObj)

    def __printUsage(self):
        printer.info(f"{self.__commandName } stands for get variable type")
        printer.info(f"Usage: {self.__commandName } <variable name>")


# !!!!! GET BASIC VARIABLE TYPE !!!!!
# Trys and returns basic type:
#   if typed was declared with using or typedef, it removes alias
class GetBaseVarType(gdb.Command):
    def __init__(self):
        super(GetBaseVarType, self).__init__(f"{commandsNamePrefix}gbvt", gdb.COMMAND_USER)
        self.__commandName = commandsNamePrefix + "gbvt"

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        argc = len(args)
        if argc != 1 or (argc == 1 and args[0] == "help"):
            self.__printUsage()
            return None
        
        try:
            type = self._getType(args[0])
            printer.data(type)
        except gdb.error as e:
            printer.error(f"Error occured: {e}")

    def _getType(self, identificator: str) -> gdb.Type:
        if commonTools.is_address(identificator):
            printer.warning("It seems like an address. Cast to a pointer to some type and try again")
            return None

        gdbObj = gdb.parse_and_eval(identificator)
        return commonTools.get_variable_basic_type(gdbObj)

    def __printUsage(self):
        printer.info(f"{self.__commandName } stands for get variable type")
        printer.info(f"Usage: {self.__commandName } <variable name>")



# !!!!! GET POLYMORPH POINTER TYPE !!!!!
# Try to parse vtable of type if it exists and returns type from vtable
class GetPolyPtrType(gdb.Command):
    def __init__(self):
        super(GetPolyPtrType, self).__init__(f"{commandsNamePrefix}gppt", gdb.COMMAND_USER)
        self.__commandName = commandsNamePrefix + "gppt"

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        argc = len(args)
        if argc != 1 or (argc == 1 and args[0] == "help"):
            self.__printUsage()
            return None
        
        try:
            type = self._getType(args[0])
            printer.data(type)
        except gdb.error as e:
            printer.error(f"Error occured: {e}")

    def _getType(self, identificator: str) -> gdb.Type:
        if commonTools.is_address(identificator):
            printer.warning("It seems like an address. Cast to a pointer to some type and try again")
            return None

        gdbObj = gdb.parse_and_eval(identificator)
        
        if commonTools.is_pointer(gdbObj):
            gdbObj = gdbObj.dereference()

        return commonTools.get_polymorh_pointer_type(gdbObj)

    def __printUsage(self):
        printer.info(f"{self.__commandName } stands for get variable type")
        printer.info(f"Usage: {self.__commandName } <variable name>")

# !!!!! GET CONTAINER'S VALUE TYPE !!!!!
# Tryes to get the value's container's type
# Doen't perform any actions on type, just print it
class GetSimpleContainerType(gdb.Command):
    def __init__(self):
        super(GetSimpleContainerType, self).__init__(f"{commandsNamePrefix}gcvt", gdb.COMMAND_USER)
        self.__commandName = commandsNamePrefix + "gcvt"

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        argc = len(args)
        if argc != 1 or (argc == 1 and args[0] == "help"):
            self.__printUsage()
        else:
            try:
                type = self._getType(args[0])
                if type['key'] == None:
                    printer.data(type['value'])
                else:
                    printer.data(f"kye: {type['key']}, value: {type['value']}")
            except Exception as e:
                printer.error(f"Error occured: {e}")

    def _getType(self, identificator: str) -> dict:

        if commonTools.is_address(identificator):
            printer.warning("It seems like an address. Cast to a pointer to some type and try again")
            return None
        
        container_value = gdb.parse_and_eval(identificator)
        return commonTools.get_container_value_type(container_value)

    def __printUsage(self):
        printer.info(f"{self.__commandName } stands for get variable type")
        printer.info(f"Usage: {self.__commandName } <variable name>")