import gdb
from ProxyInterface import ProxyInterface, NodeInterface

class ArrayNode(NodeInterface):
    def __init__(self, arrayGdb: gdb.Value, index: int = 0):
        self.array = arrayGdb
        self.index = index

    def value(self):
        if self.index >= len(self.array) or self.index < 0:
            return StopIteration
        return self.array[self.index]

    def next(self):
        return ArrayNode(self.array, self.index + 1)

    def prev(self):
        return ArrayNode(self.array, self.index - 1)


class ArrayProxy(ProxyInterface):
    def __init__(self, arrayGdb: gdb.Value, accessors: dict):
        self.arrayGdb = arrayGdb
        self.accessors = accessors
        self.array = accessors['data']


    def underlyingGdbObject(self) -> gdb.Value:
        return self.arrayGdb

    def begin(self) -> NodeInterface:
        return ArrayNode(self.array, 0)

    def end(self) -> NodeInterface:
        return ArrayNode(self.array, len(self.array) - 1)

    def element(self, index) -> NodeInterface:
        return ArrayNode(self.array, index)

    def size(self) -> int:
        return self.accessors['size']

    def containerType(self):
        return "std::array"

    def valueType(self):
        return self.accessors['valueType']