import gdb, sys, os

# current_dir = os.path.dirname(os.path.abspath(__file__))
# if current_dir not in sys.path:
#     sys.path.insert(0, current_dir)
# sys.path.append(os.path.join(current_dir, '..'))

# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(current_dir)  # Родительская директория

# # Добавляем обе директории
# if current_dir not in sys.path:
#     sys.path.insert(0, current_dir)
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

sys.path.append(os.path.join(os.path.dirname(__file__), '../Accessors'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../helpers'))

print(f"Python path: {sys.path}")  # Для отладки

from ProxyInterface import ProxyInterface, NodeInterface
from ArrayProxy import ArrayProxy, ArrayNode
from Accessors.Accessors import GlobalConfig, make_accessor
from helpers.commonTools import *
# from helpers.consts import StlContainer
import helpers.consts

# try:
#     from ProxyInterface import ProxyInterface, NodeInterface
#     from ArrayProxy import ArrayProxy, ArrayNode
#     from Accessors.Accessors import GlobalConfig, make_accessor
#     from helpers.commonTools import *
#     from helpers.consts import StlContainer
#     print("All imports successful!")
# except ImportError as e:
#     print(f"Import error: {e}")

class ContainerProxyFabric():
    def create(self, gdbObject):
        container_type = determine_container_type(gdbObject.type)
        layout = GlobalConfig().get_layout(container_type.value[0])

        template_args = get_all_template_parameters(gdbObject.type)
        accessors = dict()

        # if container_type == consts.StlContainer.ARRAY:
        #     print("##### ARRAY #####")
        #     # TODO Make valueType and size via accessors
        #     accessors['valueType'] = template_args[0]
        #     accessors['size'] = template_args[1]
        #     accessors['containerType'] = container_type.value[0]
        #     accessors['begin'] = make_accessor(layout['begin'], gdbObject)
        #     accessors['end'] = make_accessor(layout['end'], gdbObject)
        #     return ArrayProxy(gdbObject, accessors)
        # print("##### NONE #####")
        match container_type:
            case consts.StlContainer.ARRAY:
                # TODO Make valueType and size via accessors ?
                accessors['valueType'] = template_args[0]
                accessors['size'] = template_args[1]
                accessors['containerType'] = container_type.value[0]
                accessors['begin'] = make_accessor(gdbObject, layout['begin'])
                accessors['end'] = make_accessor(gdbObject, layout['end'])
                accessors['data'] = make_accessor(gdbObject, layout['data'])
                return ArrayProxy(gdbObject, accessors)
            case consts.StlContainer.VECTOR:
                accessors['valueType'] = template_args[0]
                accessors['size'] = template_args[1]
                accessors['containerType'] = container_type.value[0]
                accessors['begin'] = make_accessor(gdbObject, layout['begin'])
                accessors['end'] = make_accessor(gdbObject, layout['end'])
                accessors['data'] = make_accessor(gdbObject, layout['data'])
                return ArrayProxy(gdbObject, accessors)
        return None
