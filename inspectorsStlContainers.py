import gdb
import os
import sys
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import gdbPrinter
from commonTools import *
from consts import commandsNamePrefix
from consts import StlContainer

printer = gdbPrinter.GdbPrinter()

def get_value_type_from_definition(container: gdb.Value) -> gdb.Type:
    return container.type

def traverse_container(container: gdb.Value, containers_type: StlContainer) -> dict:
    match containers_type:
        case StlContainer.ARRAY:
            return traverse_array(container)
        case StlContainer.VECTOR:
            return traverse_vector(container)
        case StlContainer.STACK:
            return traverse_stack(container)
        case StlContainer.DEQUE:
            return traverse_deque(container)
        case StlContainer.QUEUE:
            return traverse_queue(container)
        case StlContainer.PRIOR_QUEUE:
            return traverse_prior_queue(container)
        case StlContainer.UNORD_MAP:
            return traverse_unordered_map(container)
        case StlContainer.UNORD_MULT_MAP:
            return traverse_multimap(container)
        case _:
            return {}

def traverse_array(array: gdb.Value) -> dict:
    return {i: array['_M_elems'][i] for i in range(get_array_size(array))}

    
def traverse_list(container: gdb.Value) -> dict:
    pass


def traverse_vector(vector: gdb.Value) -> dict:
    impl = vector['_M_impl']
    start = impl['_M_start']
    if not start or not impl['_M_finish']:
        return {}
    size = get_vector_size(vector)
    return {index: start[index] for index in range(size)}


def traverse_deque(deque: gdb.Value) -> dict:
    m_impl = deque['_M_impl']
    m_start = m_impl['_M_start']
    m_finish = m_impl['_M_finish']

    if not m_start or not m_finish:
        return {}
    # Получаем реальный размер deque
    # size = int(m_finish - M_start)
    size = get_deque_size(deque)
    # print(f"Expected size: {size}")

    if size == 0:
        return {}

    chunk_size_elements = int(m_start['_M_last'] - m_start['_M_first'])
    # print(f"Chunk size in elements: {chunk_size_elements}")

    current_node = m_start['_M_node']
    current = m_start['_M_cur']
    last_in_current_chunk = m_start['_M_last']

    finish_node = m_finish['_M_node']
    # finish = m_finish['_M_cur']
    finish = m_finish['_M_last']

    res = dict()
    index = 0

    while index < size:
        # Добавляем текущий элемент
        try:
            res[index] = current.dereference()
            index += 1
        except Exception as e:
            printer.error(f"Error dereferencing at index {index}: {e}")
            return {}

        current = current + 1

        if current == last_in_current_chunk and current_node != finish_node:
            current_node += 1
            current = current_node.dereference()
            last_in_current_chunk = current + chunk_size_elements

        if current_node == finish_node and current == finish:
            break

    # print(f"Actual elements collected: {len(res)}")
    return res


def traverse_container_with_underlying_container(container: gdb.Value) -> dict:
    # TODO Добавить в обработку другие возможные контейнеры
    match detect_underlying_container(container.type):
        case StlContainer.DEQUE:
            return traverse_deque(container['c'])
        case StlContainer.VECTOR:
            return traverse_vector(container['c'])
        case _:
            return {}

def traverse_stack(stack: gdb.Value) -> dict:
    # TODO Сделать вывод вершины стека и его дна
    return traverse_container_with_underlying_container(stack)

def traverse_queue(queue: gdb.Value) -> dict:
    # TODO Сделать вывод вершины и дна
    return traverse_container_with_underlying_container(queue)


def traverse_prior_queue(priority_queue: gdb.Value) -> dict:
    # TODO Сделать вывод в отсортированном виде
    return traverse_container_with_underlying_container(priority_queue)


def traverse_map(container: gdb.Value) -> dict:
    # Узнать размер мапы
    # Узнать тип значений мапы
    pass



def traverse_unordered_container(ucontainer: gdb.Value) -> dict:
    val_type = get_container_value_type(ucontainer)
    if not len(val_type):
        return {}
    val_type_str = f"std::pair<{val_type['key']} const, {val_type['value']}>"
    # pattern = r"std::__detail::_Hash_node<std::pair<.*?>, (?:true|false)>"
    hash_node_pattern = f"std::__detail::_Hash_node<{val_type_str}, (?:true|false)>"
    match = re.search(hash_node_pattern, str(ucontainer))
    if match:
        hash_node_type_str = match.group(0)
    else:
        printer.error(f"Unable to find _Hash_node type")
        return {}


    try:
        gdb_value_type = gdb.lookup_type(val_type_str)
    except gdb.error as ex:
        printer.error(f"Unexpected type {val_type_str}: {ex}")
        return {}

    try:
        gdb_hash_node_type = gdb.lookup_type(hash_node_type_str)
    except gdb.error as ex:
        printer.error(f"Unexpected type {hash_node_type_str}: {ex}")
        return {}

    m_h = ucontainer['_M_h']
    result = dict()
    try:
        elements_amount = m_h['_M_element_count']

        counter = 0

        node = m_h['_M_before_begin']['_M_nxt']

        while node or counter < elements_amount:
            next_node = node['_M_nxt']
            try:
                # Получаем значение узла
                val_ptr = node.cast(gdb_hash_node_type.pointer())
                raw_pair = val_ptr.dereference()['_M_storage']['_M_storage']['__data']
                pair = raw_pair.cast(gdb_value_type.pointer())
                maybe_string = recognize_string(pair['first'].type)
                if maybe_string == str(pair['first'].type):
                    result.setdefault(pair['first'], []).append(pair['second'])
                    # result[pair['first']] = pair['second']
                else:
                    result.setdefault(get_stl_string_value(pair['first']), []).append(pair['second'])
                    # result[get_stl_string_value(pair['first'])] = pair['second']
            except gdb.error as e:
                printer.error(f"Error occurred while parsing {node}: {e}")
                continue

            node = next_node
            counter += 1

    except gdb.error as e:
        printer.error(f"Error: {e}")
        printer.error("Maybe, another STL")
        return {}
    return result


def traverse_unordered_map(umap: gdb.Value) -> dict:
    temp_result = traverse_unordered_container(umap)
    return {key: value_list[0] for key, value_list in temp_result.items()}

def traverse_multimap(container: gdb.Value) -> dict:
    return traverse_unordered_container(container)


def traverse_unordered_multi_map(container: gdb.Value) -> dict:
    pass


def traverse_set(container: gdb.Value) -> dict:
    pass


def traverse_unordered_set(container: gdb.Value) -> dict:
    pass


def traverse_multi_set(container: gdb.Value) -> dict:
    pass


def traverse_unordered_multi_set(container: gdb.Value) -> dict:
    pass


# INSPECT
class InspectContainersValueType(gdb.Command):
    def __init__(self):
        super(InspectContainersValueType, self).__init__(f"{commandsNamePrefix}icvt", gdb.COMMAND_USER)
        self.__commandName = commandsNamePrefix + "icvt"
        self.__parsedTypes = dict()

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        argc = len(args)
        if argc != 1 or (argc == 1 and args[0] == "help"):
            self.__printUsage()
            return None

        try:
            gdb_value = gdb.parse_and_eval(args[0])
        except Exception as e:
            printer.error(f"Error occured: {e}")
            return None

        cont_type = determine_container_type(get_value_type_from_definition(gdb_value))
        res = traverse_container(gdb_value, cont_type)
        if not len(res):
            printer.error(f"{args[0]} is empty or corrupted")
        for index, value in res.items():
            # TODO Сделать функции для корректной печати разных контейнеров
            if isinstance(value, list):
                printer.data(f"{index}:")
                for val in value:
                    var_type = get_variable_type(val)
                    base_type = get_variable_basic_type(val)
                    poly_type = get_polymorh_pointer_type(val)
                    printer.data(f"|_\t{val} --> {var_type} : {base_type} : {poly_type}")
            else:
                var_type = get_variable_type(value)
                base_type = get_variable_basic_type(value)
                poly_type = get_polymorh_pointer_type(value)
                printer.data(f"{index}: {value} --> {var_type} : {base_type} : {poly_type}")

    def __printUsage(self):
        printer.info(f"{self.__commandName } stands for inspect container's value type")
        printer.info(f"Usage: {self.__commandName } <variable name>")

InspectContainersValueType()