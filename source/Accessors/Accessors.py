import gdb
import yaml
import os
import sys

from abc import ABC, abstractmethod

class GlobalConfig:
    _instance = None
    _compiler = "g++13.3.0"
    _config = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, path: str = "/home/oppo/Projects/gdbTools/test/config.yaml", compiler: str = "") -> None:
        if compiler:
            self._compiler = compiler
        # TODO read all files in directory "config"
        with open(path, "r") as f:
            self._config = yaml.load(f, Loader=yaml.SafeLoader)

        if not hasattr(self, '_initialized'):
            self._initialized = True

    def get_layout(self, type: str) -> dict:
        return self._config[self._compiler][type]

class ValueAccessor:
    def __init__(self, data: gdb.Value):
        self._data = data

    @abstractmethod
    def operation(self):
        return self._data

class StepDecorator(ValueAccessor):
    """Базовый класс декоратора"""
    def __init__(self, data: gdb.Value, key: str):
        super().__init__(data)
        self._key = key

class FieldStep(StepDecorator):
    def operation(self):
        data = self._data.operation()
        return data[self._key]


def make_accessor(layout: str, data: gdb.Value, key: str = "") -> ValueAccessor:
    layout_steps = layout.split(':')[:-1] # cut out the last element which must be value
    accessor = ValueAccessor(data)

    if key:
        for step in layout_steps:
            if step != key:
                accessor = FieldStep(accessor, key=step)
            else:
                break
    else:
        for step in layout_steps:
            accessor = FieldStep(accessor, key=step)
    return accessor