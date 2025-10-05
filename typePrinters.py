import gdb
import os
import sys

import commonTools

# TODO Реализовать

class StringTypePrinter:
    def __init__(self):
        self.enabled = True
        self.name = "std_string_typedef_printer"

    def instantiate(self):
        return StringRecognizer()


class StringRecognizer:
    def recognize(self, gdb_type) -> str:
        return commonTools.recognize_string(gdb_type)