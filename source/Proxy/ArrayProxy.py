import gdb, os, sys
from gi.overrides.keysyms import value

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from ProxyInterface import ProxyInterface, NodeInterface

class ArrayNode(NodeInterface):
    def __init__(self, arrayGdb: gdb.Value, index: int = 0):
        self.array = arrayGdb
        self.index = index

    def __str__(self):
        return f"<ArrayNode -- index: {self.index}, array: {self.array}>"

    def value(self):
        # if self.index >= len(self.array) or self.index < 0:
        #     return StopIteration
        val = self.array[self.index]
        if val.type.code == gdb.TYPE_CODE_INT:
            return int(val)
        elif val.type.code == gdb.TYPE_CODE_FLT:
            return float(val)
        elif val.type.code == gdb.TYPE_CODE_STRING:
            return str(val)
        # elif val.type.code == gdb.TYPE_CODE_PTR:
        #     return hex(int(val)) if int(val) != 0 else None
        elif val.type.code == gdb.TYPE_CODE_BOOL:
            return bool(val)
        return val


    def next(self):
        return ArrayNode(self.array, self.index + 1)

    def prev(self):
        return ArrayNode(self.array, self.index - 1)



class ArrayProxy(ProxyInterface):
    def __init__(self, array_gdb: gdb.Value, accessors: dict):
        self.arrayGdb = array_gdb
        self.accessors = accessors
        self.array = accessors['data'].operation()

    def __str__(self):
        return f"<ArrayProxy -- array: {self.array}>"


    def underlying_gdb_object(self) -> gdb.Value:
        return self.arrayGdb

    def begin(self) -> NodeInterface:
        return ArrayNode(self.array, 0)

    def end(self) -> NodeInterface:
        return ArrayNode(self.array, self.size() - 1)

    def element(self, index) -> NodeInterface:
        return ArrayNode(self.array,  index)

    def size(self) -> int:
        return self.accessors['size']

    def container_type(self):
        return "std::array"

    def value_type(self):
        return self.accessors['valueType']