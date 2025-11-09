from ProxyInterface import ProxyInterface, NodeInterface
from ArrayProxy import ArrayProxy, ArrayNode

import gdb, sys, os
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    sys.path.append(os.path.join(current_dir, '..'))

from ..Accessors.Accessors import GlobalConfig, make_accessor
from ..helpers.commonTools import *
from ..helpers.consts import StlContainer

class ContainerProxyFabric():
    def create(self, gdbObject):
        containerType = determine_container_type(gdbObject.type)
        layout = GlobalConfig().get_layout(containerType.keys()[0])

        template_args = get_all_template_parameters(gdbObject.type)
        accessors = dict()

        type = containerType.values()[0]
        match type:
            case StlContainer.ARRAY:
                # TODO Make valueType and size via accessors
                accessors['valueType'] = template_args[0]
                accessors['size'] = template_args[1]
                accessors['containerType'] = containerType.keys()[0]
                accessors['begin'] = make_accessor(layout['begin'], gdbObject)
                accessors['end'] = make_accessor(layout['end'], gdbObject)
                return ArrayProxy(gdbObject, accessors)