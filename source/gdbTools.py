import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from helpers.gdbPrinter import GdbPrinter
from typesGetters import GetVarType, GetBaseVarType, GetPolyPtrType, GetSimpleContainerType
from viewerStlContainers import InspectContainersValueType

__all__ = ['InspectContainersValueType', 'GetVarType', 'GetBaseVarType', 'GetPolyPtrType', 'GetSimpleContainerType',
           'printer']

printer = GdbPrinter()

GetVarType()
GetBaseVarType()
GetPolyPtrType()
GetSimpleContainerType()

InspectContainersValueType()

printer.info("GDB tools loaded successfully")

