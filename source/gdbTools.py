import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from helpers.gdbPrinter import GdbPrinter
from help import Info, Help
from cacher import CacheList, CacheGet, CacheDelete, CacheClear
from typesGetters import GetVarType, GetBaseVarType, GetPolyPtrType, GetSimpleContainerType
from viewerStlContainers import InspectContainersValueType

__all__ = ['Info', 'Help', 'CacheList', 'CacheGet', 'CacheDelete', 'CacheClear',  'InspectContainersValueType', 'GetVarType', 'GetBaseVarType'
    , 'GetPolyPtrType', 'GetSimpleContainerType', 'printer']

printer = GdbPrinter()

# Help
Info()
Help()

# Cacher
CacheList()
CacheGet()
CacheDelete()
CacheClear()

# Type getters
GetVarType()
GetBaseVarType()
GetPolyPtrType()
GetSimpleContainerType()

# Stl container viewer
InspectContainersValueType()


printer.info("GDB tools loaded successfully\nUse gdbTools-info for info\nUse gdbTools-help for help")

