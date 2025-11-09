import gdb
import os
import sys
from abc import ABC, abstractmethod

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    sys.path.append(os.path.join(current_dir, '..'))

from ..Accessors.Accessors import make_accessor
from ..Accessors.Accessors import ValueAccessor

class Iterator:
    def __init__(self, data: gdb.Value, operation):
        self._data = data
        self._operation = operation
        self._index = -1
        self._current_value = None

    def next(self):
        return self.__next__()

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    @abstractmethod
    def value(self):
        pass

class AccessIterator:
    def __init__(self, accessor: ValueAccessor, operation):
        self._accessor = accessor
        self._operation = operation
        self._index = -1
        self._current_value = None

    def next(self):
        return self.__next__()

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    @abstractmethod
    def value(self):
        pass

class FilterIterator(Iterator):
    def __init__(self, data: gdb.Value, size:int, operation):
        super().__init__(data, operation)
        self._size = size
        self._index = 0

    def __next__(self):
        if self._index >= self._size:
            raise StopIteration

        if not self._operation(self._data[self._index]):
            while self._index < self._size and not self._operation(self._data[self._index]):
                self._index += 1
        else:
            self._index += 1

        if self._index >= self._size:
            raise StopIteration
        self._current_value = self._data[self._index]
        return self._current_value


    def value(self):
        return self._current_value

class ArrayIterator(AccessIterator):
    def __init__(self, accessor: ValueAccessor, operation = None):
        super().__init__(accessor, operation)
        self._index = 0

    def __next__(self):
        if self._index >= self._size:
            raise StopIteration
        self._current_value = self._data[self._index]
        self._index += 1
        if self._operation is not None:
            self._current_value = self._operation(self._current_value)
        return self._current_value

    def value(self):
        return self._current_value

# class ArrayIterator(Iterator):
#     def __init__(self, data: gdb.Value, size:int, operation = None):
#         super().__init__(data, operation)
#         self._size = size
#         self._index = 0
#
#     def __next__(self):
#         if self._index >= self._size:
#             raise StopIteration
#         self._current_value = self._data[self._index]
#         self._index += 1
#         if self._operation is not None:
#             self._current_value = self._operation(self._current_value)
#         return self._current_value
#
#     def value(self):
#         return self._current_value
