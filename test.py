import gdb

import commonTools

class Test(gdb.Command):
    def __init__(self):
        super(Test, self).__init__(f"TEST", gdb.COMMAND_USER)

    def invoke(self, argument, from_tty):
        print(commonTools.get_stl_string_value(gdb.parse_and_eval("tmp2")))

Test()