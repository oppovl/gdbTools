import gdb, argparse, os, sys, yaml

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from helpers.consts import commandsNamePrefix
from helpers.commonTools import *
from helpers.gdbPrinter import printer
from cacher import cache

# from Proxy.ArrayProxy import ArrayProxy
from Proxy.ContainerProxyFabric import ContainerProxyFabric

from Accessors.Accessors import make_accessor
from Accessors.Accessors import GlobalConfig

def make_array_iterator(array: gdb.Value) -> dict:
    lyaout = GlobalConfig().get_layout("std::array")
    return {i: array['_M_elems'][i] for i in range(get_array_size(array))}


def traverse_list(stdlist: gdb.Value) -> dict:
    template_args_type = get_container_value_type(stdlist)
    value_type = template_args_type['value']
    if not len(template_args_type):
        return {}

    str_node_type = f"std::_List_node<{template_args_type['value']}>"
    try:
        gdb_node_type = gdb.lookup_type(str_node_type)
    except gdb.error as err:
        printer.error(f"Error looking type {str_node_type}: {err}")
        return {}
    except Exception as err:
        printer.error(f"Error occurred: {err}")
        return {}

    size = stdlist['_M_impl']['_M_node']['_M_size']
    node = stdlist['_M_impl']['_M_node']['_M_next']
    result = dict()
    for i in range(size):
        list_node = node.cast(gdb_node_type.pointer()).dereference()
        storage = list_node['_M_storage']['_M_storage']
        value = storage.cast(value_type.pointer()).dereference()
        result[i] = value
        node = node['_M_next']
    return result


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
    # size = int(m_finish - M_start)
    size = get_deque_size(deque)

    if size == 0:
        return {}

    chunk_size_elements = int(m_start['_M_last'] - m_start['_M_first'])

    current_node = m_start['_M_node']
    current = m_start['_M_cur']
    last_in_current_chunk = m_start['_M_last']

    finish_node = m_finish['_M_node']
    # finish = m_finish['_M_cur']
    finish = m_finish['_M_last']

    res = dict()
    index = 0

    while index < size:
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

    return res


def traverse_container_with_underlying_container(container: gdb.Value) -> dict:
    # TODO Another containers
    match detect_underlying_container(container.type):
        case consts.StlContainer.DEQUE:
            return traverse_deque(container['c'])
        case consts.StlContainer.VECTOR:
            return traverse_vector(container['c'])
        case _:
            return {}

def traverse_stack(stack: gdb.Value) -> dict:
    # TODO Sort from top to bottom if unsorted
    return traverse_container_with_underlying_container(stack)

def traverse_queue(queue: gdb.Value) -> dict:
    # TODO Sort from top to bottom if unsorted
    return traverse_container_with_underlying_container(queue)


def traverse_prior_queue(priority_queue: gdb.Value) -> dict:
    # TODO Sort values
    return traverse_container_with_underlying_container(priority_queue)


def traverse_tree_container(tree: gdb.Value, containers_kind: consts.StlContainer) -> dict:
    value_type = get_container_value_type(tree)
    if not len(value_type):
        return {}
    str_value_type = f"std::pair<{value_type['key']} const, {value_type['value']}>"
    match containers_kind:
        case consts.StlContainer.SET | consts.StlContainer.MULT_SET:
            str_value_type = str(value_type['value'])
        case _:
            pass

    try:
        gdb_value_type = gdb.lookup_type(str_value_type)
    except gdb.error as err:
        printer.error(f"Error looking type {str_value_type}: {err}")
        return {}

    root_node = tree['_M_t']['_M_impl']['_M_header']['_M_parent']

    str_node_type = f'std::_Rb_tree_node<{str_value_type}>'
    try:
        gdb_node_type = gdb.lookup_type(str_node_type)
    except gdb.error as err:
        printer.error(f"Error looking type {str_node_type}: {err}")
        return {}

    node = root_node.cast(gdb_node_type.pointer())
    if not node:
        return {}

    res = dict()
    traverse_tree(tree, containers_kind, node, gdb_node_type, gdb_value_type, res)
    return res


def traverse_tree(tree: gdb.Value, containers_kind: consts.StlContainer, node: gdb.Value, node_type: gdb.Type, value_type: gdb.Type, result: dict) -> None:
    node = node.cast(node_type.pointer())
    if not node:
        return None

    pair = node.dereference()['_M_storage']['_M_storage'].cast(value_type.pointer()).dereference()

    match containers_kind:
        case consts.StlContainer.SET | consts.StlContainer.MULT_SET:
            result.setdefault(len(result), []).append(pair)
        case _:
            print(pair['first'])
            key = get_string_if_string_or_default(pair['first'], pair['first'])
            value = get_string_if_string_or_default(pair['second'], pair['second'])
            result.setdefault(key, []).append(value)

    traverse_tree(tree, containers_kind, node['_M_left'], node_type, value_type, result)
    traverse_tree(tree, containers_kind, node['_M_right'], node_type, value_type, result)

    return None



def traverse_map(m: gdb.Value) -> dict:
    tree_result = traverse_tree_container(m, consts.StlContainer.MAP)
    return {key: value_list[0] for key, value_list in tree_result.items()}


def traverse_multimap(multimap: gdb.Value) -> dict:
    return traverse_tree_container(multimap, consts.StlContainer.MULT_MAP)


def traverse_unordered_container(ucontainer: gdb.Value, containers_kind: consts.StlContainer) -> dict:
    val_type = get_container_value_type(ucontainer)
    if not len(val_type):
        return {}
    val_type_str = f"std::pair<{val_type['key']} const, {val_type['value']}>"
    match containers_kind:
        case consts.StlContainer.UNORD_SET | consts.StlContainer.UNORD_MULT_SET:
            val_type_str = str(val_type['value'])
        case _:
            pass

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
                val_ptr = node.cast(gdb_hash_node_type.pointer())
                raw_pair = val_ptr.dereference()['_M_storage']['_M_storage']['__data']
                pair = raw_pair.cast(gdb_value_type.pointer()).dereference()
                match containers_kind:
                    case consts.StlContainer.UNORD_SET | consts.StlContainer.UNORD_MULT_SET:
                        result.setdefault(len(result), []).append(pair)
                    case _:
                        key = get_string_if_string_or_default(pair['first'], pair['first'])
                        value = get_string_if_string_or_default(pair['second'], pair['second'])
                        result.setdefault(key, []).append(value)

                # key = get_string_if_string_or_default(pair['first'], pair['first'])
                # value = get_string_if_string_or_default(pair['second'], pair['second'])
                # result.setdefault(key, []).append(value)
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
    temp_result = traverse_unordered_container(umap, consts.StlContainer.UNORD_MAP)
    return {key: value_list[0] for key, value_list in temp_result.items()}


def traverse_unordered_multimap(unordered_multi_map: gdb.Value) -> dict:
    return traverse_unordered_container(unordered_multi_map, consts.StlContainer.UNORD_MULT_MAP)


def traverse_set(stdset: gdb.Value) -> dict:
    result = traverse_tree_container(stdset, consts.StlContainer.SET)
    return {key: value_list[0] for key, value_list in result.items()}


def traverse_multiset(multiset: gdb.Value) -> dict:
    return traverse_tree_container(multiset, consts.StlContainer.MULT_SET)


def traverse_unordered_set(uset: gdb.Value) -> dict:
    result = traverse_unordered_container(uset, consts.StlContainer.UNORD_SET)
    return {key: value[0] for key, value in result.items()}


def traverse_unordered_multiset(umultiset: gdb.Value) -> dict:
    return traverse_unordered_container(umultiset, consts.StlContainer.UNORD_MULT_SET)

def create_lambda_filter(expr: str, container_value_type):
    if expr == None:
        return lambda x: True
    validation_pattern = r'^(<=|>=|==|!=|<|>)\S+$'
    if not re.match(validation_pattern, expr):
        return lambda x: True

    parsing_pattern = r'^(<=|>=|==|!=|<|>)(.+)$'

    match = re.match(parsing_pattern, expr)
    if match:
        operator = match.group(1)
        value = match.group(2)
    else:
        return lambda x: True

    converter = lambda x: x
    if container_value_type.code == gdb.TYPE_CODE_INT:
        converter = lambda x: int(x)
    elif container_value_type.code == gdb.TYPE_CODE_FLT:
        converter = lambda x:  float(x)
    elif container_value_type.code == gdb.TYPE_CODE_STRING:
        converter = lambda x:  str(x)
    # elif container_value_type.code == gdb.TYPE_CODE_PTR:
    #     return hex(int(val)) if int(val) != 0 else None
    elif container_value_type.code == gdb.TYPE_CODE_BOOL:
        converter = lambda x:  bool(x)

    match operator:
        case '<=':
            return lambda x: x <= converter(value)
        case '>=':
            return lambda x: x >= converter(value)
        case '<':
            return lambda x: x < converter(value)
        case '>':
            return lambda x: x > converter(value)
        case '==':
            return lambda x: x == converter(value)
        case '!=':
            return lambda x: x != converter(value)

    return lambda x: True


# INSPECT
class InspectValues(gdb.Command):
    def __init__(self):
        super(InspectValues, self).__init__(f"{commandsNamePrefix}iv", gdb.COMMAND_USER)
        self.__commandName = commandsNamePrefix + "iv"

    def invoke(self, arg, from_tty):
        # TODO Move the parser outside the command and create it only once
        parser = argparse.ArgumentParser()
        parser.add_argument('input', type=str, help='Name of variable')

        parser.add_argument('--config', '-c', type=str, help='Name of class description from config file')

        parser.add_argument('--key', '-k', type=str, help="Field's name of class objects which is keys")
        parser.add_argument('--value', '-v', type=str, help="Field's name of class objects which is values")

        parser.add_argument('--key_acc', '-ka', type=str, help="Access layout")
        parser.add_argument('--value_acc', '-va', type=str, help="Access layout")

        parser.add_argument('--cache', action='store_true', help="Caches results")
        parser.add_argument('--store', '-s', type=str, help="Stores results to a variable")

        args = parser.parse_args(arg.split())

        try:
            gdb_value = gdb.parse_and_eval(args.input)
        except Exception as e:
            printer.error(f"Error occured: {e}")
            return None

        arrayProxy = ContainerProxyFabric().create(gdb_value)

        key_filter = create_lambda_filter(args.key, arrayProxy.value_type())
        value_filter = create_lambda_filter(args.value, arrayProxy.value_type())



        node = arrayProxy.begin()
        values = list()
        for i in range(arrayProxy.size()):
            val = node.value()
            if args.key_acc:
                key_accessor = make_accessor(args.key_acc)
            if args.key_acc:
                value_accessor = make_accessor(args.key_acc)
            values.append(val)
            node = node.next()


        if type(values[0]) == dict:
            values[:] = filter(key_filter, values)
        values[:] = filter(value_filter, values)
        printer.data(values)


        # filtered_values = filter(my_filter, values)

        # printer.warning("#####")
        # printer.warning(begin.next().value())
        # printer.warning(arrayProxy.end().prev().value())

        return None


    def __printUsage(self):
        printer.info(f"{self.__commandName } stands for inspect value")
        printer.info(f"Usage: {self.__commandName } <variable name>")