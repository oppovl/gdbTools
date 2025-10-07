import gdb

class Cacher:
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