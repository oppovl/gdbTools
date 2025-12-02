import gdb
from abc import ABC, abstractmethod

class NodeInterface(ABC):
    def __str__(self):
        return "<NodeInterface>"
    @abstractmethod
    def next(self):
        pass

    @abstractmethod
    def prev(self):
        pass

    @abstractmethod
    def value(self):
        pass

class ProxyInterface(ABC):
    def __str__(self):
        return "<ProxyInterface>"

    @abstractmethod
    def underlying_gdb_object(self) -> gdb.Value:
        pass

    @abstractmethod
    def begin(self) -> NodeInterface:
        pass

    @abstractmethod
    def end(self) -> NodeInterface:
        pass

    @abstractmethod
    def element(self, index) -> NodeInterface:
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def container_type(self):
        pass

    @abstractmethod
    def value_type(self):
        pass
