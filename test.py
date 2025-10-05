import gdb

import commonTools

class Test(gdb.Command):
    def __init__(self):
        super(Test, self).__init__(f"TEST", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        argc = len(args)
        lst = list()
        m = gdb.parse_and_eval(args[0])
        rootNode = m['_M_t']['_M_impl']['_M_header']['_M_parent']
        traverseTree(lst, rootNode, "std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, int>", False)
        print(len(lst))
        print(lst)

Test()


def __collectWsNodesFromMap(self, map: gdb.Value, container, pairType, toPrint=False):
    rootNode = map['_M_t']['_M_impl']['_M_header']['_M_parent']
    # rootNode = rootNode.dereference()
    self._traverseTree(container, rootNode, pairType, toPrint)
    leftAmount = len(container)
    if toPrint:
        print(f"Nodes in left branch: {leftAmount}")
    if toPrint:
        print(f"Nodes in right branch: {len(container) - leftAmount}")


def traverseTree(container, rootNode, pairType, toPrint):
    if rootNode in container:
        return
    node = rootNode.cast(gdb.lookup_type(f'std::_Rb_tree_node<{pairType}>').pointer())
    if not node:
        return

    storagePair = node.dereference()['_M_storage']['_M_storage'].cast(
        gdb.lookup_type(pairType).pointer()).dereference()
    key = storagePair['first']
    value = storagePair['second']
    container.append(int(value))
    if toPrint:
        print(f"[{key}] --> {value}")
        print('-' * 50)

    # Рекурсивный обход дерева
    traverseTree(container, node['_M_left'], pairType, toPrint)
    traverseTree(container, node['_M_right'], pairType, toPrint)


def _inspectWsConnectionCallLogics(self, upWsConnection):
    rawPtr = upWsConnection['_M_t']['_M_t']['_M_head_impl']
    wsConnection = rawPtr.cast(gdb.lookup_type('asbc::WebSocketConnection').pointer()).dereference()
    callLogicsMap = wsConnection['m_callLogics']
    if callLogicsMap['_M_t']['_M_impl']['_M_node_count'] == 0:
        return
    collectedWsCallLogics = set()
    self.__collectWsNodesFromMap(callLogicsMap, collectedWsCallLogics, self.wsCallLogicPairType)
    # print(f"WsConnection {wsConnection.address} is containing {callLogicsMap['_M_t']['_M_impl']['_M_node_count']} asbc::WebSocketCallLogic; collected {len(collectedWsCallLogics)}")
    self._inspectWsCallLogicsForCoreId(collectedWsCallLogics)

