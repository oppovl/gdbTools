import gdb
import re
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import consts

def is_pointer(variable: gdb.Value) -> bool:
    return variable.type.code is gdb.TYPE_CODE_PTR

def is_address(nameOrAddress: str) -> bool:
    m = re.match('0x[a-zA-Z0-9]{8,16}', nameOrAddress)
    if m:
        return True
    return False


def recognize_string(gdb_type: gdb.Type) -> str:
    basic_type = gdb_type.strip_typedefs()
    basic_type_str = str(basic_type)
    return consts.typedef_stl_strings_map.get(delete_extra_spaces_in_type_str(basic_type_str)
                                              , basic_type_str)


def delete_extra_spaces_in_type_str(string: str) -> str:
    return string.replace(' ', '')


def get_stl_string_value(gdb_string_obj: gdb.Value) -> str:
    return gdb_string_obj['_M_dataplus']['_M_p'].string()


def get_string_if_string_or_default(value: gdb.Value, default):
    maybe_string = recognize_string(value.type)
    print(maybe_string)
    print(str(value.type))
    if maybe_string == str(value.type):
        return default
    else:
        return get_stl_string_value(value)

def determine_container_type(containerGdbType: gdb.Type) -> consts.StlContainer:
    match = re.search(r'std::[^<]+', str(containerGdbType))

    if not match:
        return consts.StlContainer.UNKNOWN
    
    container_str_type = match.group(0)

    match container_str_type:
            case 'std::array':
                return consts.StlContainer.ARRAY
            case 'std::list' | 'std::__cxx11::list':
                return consts.StlContainer.LIST
            case 'std::vector':
                return consts.StlContainer.VECTOR
            case 'std::stack':
                return consts.StlContainer.STACK
            case 'std::deque':
                return consts.StlContainer.DEQUE
            case 'std::queue':
                return consts.StlContainer.QUEUE
            case 'std::priority_queue':
                return consts.StlContainer.PRIOR_QUEUE
            case 'std::map':
                return consts.StlContainer.MAP
            case 'std::unordered_map':
                return consts.StlContainer.UNORD_MAP
            case 'std::multimap':
                return consts.StlContainer.MULT_MAP
            case 'std::unordered_multimap':
                return consts.StlContainer.UNORD_MULT_MAP
            case 'std::set':
                return consts.StlContainer.SET
            case 'std::multiset':
                return consts.StlContainer.MULT_SET
            case 'std::unordered_set':
                return consts.StlContainer.UNORD_SET
            case 'std::unordered_multiset':
                return consts.StlContainer.UNORD_MULT_SET
            case _:
                return None
        

def get_variable_type(value: gdb.Value) -> gdb.Type:
    return value.type

def get_variable_basic_type(value: gdb.Value) -> gdb.Type:
    return gdb.types.get_basic_type(value.type)

def get_polymorh_pointer_type(value: gdb.Value) -> gdb.Type:
    pattern = r"_vptr\.\w+ = 0x[0-9a-f]+ <vtable for ([^+>]+)"
    obj_str = str(value)
    match = re.search(pattern, obj_str)
    
    if match:
        str_type = match.group(1)
        return gdb.lookup_type(str_type)
    return None


def detect_underlying_container(mainContainerType: gdb.Type) -> consts.StlContainer:
    match = re.search(r'std::(?:stack|queue|priority_queue)<[^,]+,\s*(std::\w+)<', str(mainContainerType))

    if not match:
        return consts.StlContainer.UNKNOWN

    container_str_type = match.group(1)

    match container_str_type:
            case 'std::array':
                return consts.StlContainer.ARRAY
            case 'std::list':
                return consts.StlContainer.LIST
            case 'std::vector':
                return consts.StlContainer.VECTOR
            case 'std::stack':
                return consts.StlContainer.STACK
            case 'std::deque':
                return consts.StlContainer.DEQUE
            case 'std::queue':
                return consts.StlContainer.QUEUE
            case 'std::priority_queue':
                return consts.StlContainer.PRIOR_QUEUE
            case 'std::map':
                return consts.StlContainer.MAP
            case 'std::unordered_map':
                return consts.StlContainer.UNORD_MAP
            case 'std::multimap':
                return consts.StlContainer.MULT_MAP
            case 'std::unordered_multimap':
                return consts.StlContainer.UNORD_MULT_MAP
            case 'std::set':
                return consts.StlContainer.SET
            case 'std::multiset':
                return consts.StlContainer.MULT_SET
            case 'std::unordered_set':
                return consts.StlContainer.UNORD_SET
            case 'std::unordered_multiset':
                return consts.StlContainer.UNORD_MULT_SET
            case _:
                return consts.StlContainer.UNKNOWN

def get_container_value_type(container: gdb.Value) -> dict:
    match determine_container_type(container.type):
        case consts.StlContainer.VECTOR:
            return get_one_template_arg(container.type)
        case consts.StlContainer.LIST:
            return get_one_template_arg(container.type)
        case consts.StlContainer.ARRAY:
            return get_one_template_arg(container.type)
        case consts.StlContainer.DEQUE:
            return get_one_template_arg(container.type)
        case consts.StlContainer.QUEUE:
            return get_one_template_arg(container.type)
        case consts.StlContainer.PRIOR_QUEUE:
            return get_one_template_arg(container.type)
        case consts.StlContainer.STACK:
            return get_one_template_arg(container.type)
        case consts.StlContainer.MAP:
            return get_two_template_arg(container.type)
        case consts.StlContainer.MULT_MAP:
            return get_two_template_arg(container.type)
        case consts.StlContainer.UNORD_MAP:
            return get_two_template_arg(container.type)
        case consts.StlContainer.UNORD_MULT_MAP:
            return get_two_template_arg(container.type)
        case consts.StlContainer.SET:
            return get_one_template_arg(container.type)
        case consts.StlContainer.MULT_SET:
            return get_one_template_arg(container.type)
        case consts.StlContainer.UNORD_SET:
            return get_two_template_arg(container.type)
        case consts.StlContainer.UNORD_MULT_SET:
            return get_two_template_arg(container.type)
        case _:
            return dict()

def get_one_template_arg(container_type: gdb.Type) -> dict:
    return {"key": None, "value": container_type.template_argument(0)}

def get_two_template_arg(container_type: gdb.Type) -> dict:
    return {"key": container_type.template_argument(0), "value": container_type.template_argument(1)}

# TODO deprecated?
def type_from_type_str(type_str: str) -> str:
    match = re.search(r'std::[^<]+', type_str)
    if match:
        return match.group(0)
    return str()

def get_container_size(container: gdb.Value, cont_type: consts.StlContainer) -> int:
    match cont_type:
        case consts.StlContainer.ARRAY:
            return get_array_size(container)
        case consts.StlContainer.VECTOR:
            return get_vector_size(container)
        case _:
            return -1


def get_array_size(array: gdb.Value) -> int:
    return int(array.type.template_argument(1))

def get_vector_size(vector: gdb.Value) -> int:
    return int(vector['_M_impl']['_M_finish'] - vector['_M_impl']['_M_start'])
    
def get_stack_size(stack: gdb.Value) -> int:
    # См. traversStack
    # Не используется
    pass

def get_deque_size(deque: gdb.Value) -> int:
    return int(deque['_M_impl']['_M_finish'] - deque['_M_impl']['_M_start'])