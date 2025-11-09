from abc import ABC, abstractmethod

class NodeInterface(ABC):
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
    @abstractmethod
    def underlyingGdbObject(self) -> gdb.Value:
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
    def containerType(self):
        pass

    @abstractmethod
    def valueType(self):
        pass
