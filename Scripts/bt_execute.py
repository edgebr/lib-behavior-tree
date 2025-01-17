#Behavior Tree like Tree.
INDEX_NODE_TYPE = 1
INDEX_NODE_CHILDREN = 2
INDEX_NODE_TARGET = 4
INDEX_NODE_SIBLING = -2
INDEX_NODE_PARENT = -1
INDEX_NODE_FUNCTION = 2
INDEX_NODE_DECORATOR_POINTER = 2
INDEX_NODE_DECORATOR_NUM_ATTEMPTS = 3
INDEX_NODE_DECORATOR_TARGET = 4
INDEX_NODE_DECORATOR_PARENT = 5

#Tree like DAG
INDEX_OF_POSITION = 0
INDEX_SUCCESS_CASE = 2
INDEX_FAIL_CASE = 3
INDEX_POINTER_VERIFY = -1

#Node invalid
NODE_UNRELATED = "BT_DEFINITION_TREE_UNRELATED"

#Macros of nodes
macro_node_condition = "BT_DEFINITION_CREATE_NODE_CONDITION"
macro_node_action = "BT_DEFINITION_CREATE_NODE_ACTION"
macro_node_retry_until_success = "BT_DEFINITION_CREATE_NODE_RETRY_UNTIL_SUCCESS"
macro_node_reactive_condition = "BT_DEFINITION_CREATE_NODE_REACTIVE_CONDITION"
macro_node_reactive_action = "BT_DEFINITION_CREATE_NODE_REACTIVE_ACTION"
macro_node_reactive_retry_until_success = "BT_DEFINITION_CREATE_NODE_REACTIVE_RETRY_UNTIL_SUCCESS"

#Status of nodes
status_node = [ 'success', 'fail']
status_fail = 'fail'
status_success = 'success'
status_running = 'Running'

class BT_EXECUTE:
    def __init__(self):
        self.node_root = 'Root'
        self.node_sequence = 'Sequence'
        self.node_fallback = 'Fallback'
        self.node_reactive_sequence = 'ReactiveSequence'
        self.node_reactive_fallback = 'ReactiveFallback'
        self.node_action = 'Script'
        self.node_condition = 'ScriptCondition'
        self.node_subtree = 'SubTree'
        self.tree_status = status_running
        self.node_retry_until_successful = 'RetryUntilSuccessful'
        self.next_node = 0
        self.nodes_path = []

    def is_decorator_node(self, node_type):
        return ((node_type == macro_node_retry_until_success) or (node_type == macro_node_reactive_retry_until_success))

    def get_nodes_name(self, node_root = None, node_fallback = None, node_reactive_fallback = None, 
                       node_sequence = None, node_reactive_sequence = None, 
                       node_action = None, node_condition = None, node_retry_until_successful = None, 
                       node_delay = None, node_subtree = None):
        self.node_root = node_root
        self.node_fallback = node_fallback
        self.node_reactive_fallback = node_reactive_fallback
        self.node_sequence = node_sequence
        self.node_reactive_sequence = node_reactive_sequence
        self.node_action = node_action
        self.node_condition = node_condition
        self.node_retry_until_successful = node_retry_until_successful
        self.node_delay = node_delay
        self.node_subtree = node_subtree

    def process_node(self, node, node_status):
        if node[INDEX_NODE_TYPE] == self.node_root:
            if((self.tree_status == status_success) or (self.tree_status == status_fail)):
                return self.tree_status
            self.next_node = node[INDEX_NODE_SIBLING]
        elif ((node[INDEX_NODE_TYPE] == self.node_sequence) or (node[INDEX_NODE_TYPE] == self.node_fallback)):
            if self.tree_status == status_running:
                self.next_node = node[INDEX_NODE_CHILDREN]
                return status_running
            node_status = self.tree_status
        elif ((node[INDEX_NODE_TYPE] == self.node_reactive_sequence) or (node[INDEX_NODE_TYPE] == self.node_reactive_fallback)):
            if self.tree_status == status_running:
                self.next_node = node[INDEX_NODE_CHILDREN]
                return status_running
            node_status = self.tree_status
        if (((self.tree[node[INDEX_NODE_PARENT]][INDEX_NODE_TYPE] == self.node_fallback) and (node_status == status_success)) or 
              ((self.tree[node[INDEX_NODE_PARENT]][INDEX_NODE_TYPE] == self.node_sequence) and (node_status == status_fail)) or 
              ((self.tree[node[INDEX_NODE_PARENT]][INDEX_NODE_TYPE] == self.node_reactive_fallback) and (node_status == status_success)) or 
              ((self.tree[node[INDEX_NODE_PARENT]][INDEX_NODE_TYPE] == self.node_reactive_sequence) and (node_status == status_fail)) or 
              ((node[INDEX_NODE_SIBLING] == NODE_UNRELATED))) :
            self.next_node = node[INDEX_NODE_PARENT]
            self.tree_status = node_status
        else:            
            self.tree_status = status_running
            self.next_node = node[INDEX_NODE_SIBLING]
        return status_running        
        
    def init_process(self, tree):
        self.tree = tree
        index = 0
        for i in range(len(tree)):
            if((tree[i][INDEX_NODE_TYPE] == self.node_condition) or
               (tree[i][INDEX_NODE_TYPE] == self.node_action) or
               (tree[i][INDEX_NODE_TYPE] == self.node_retry_until_successful)):
                value = []
                for status in status_node:
                    status_tree = self.process_node(tree[i], status)
                    while((tree[self.next_node][INDEX_NODE_TYPE] != self.node_root) and
                          (tree[self.next_node][INDEX_NODE_TYPE] != self.node_condition) and
                          (tree[self.next_node][INDEX_NODE_TYPE] != self.node_action) and
                          (tree[self.next_node][INDEX_NODE_TYPE] != self.node_retry_until_successful) and
                          (status_tree == status_running)):
                        self.process_node(tree[self.next_node], self.tree_status)
                    value.append(self.next_node)
                if ((tree[tree[i][INDEX_NODE_PARENT]][INDEX_NODE_TYPE] == self.node_reactive_sequence) or \
                    (tree[tree[i][INDEX_NODE_PARENT]][INDEX_NODE_TYPE] == self.node_reactive_fallback)):
                    is_reactive = True
                else:
                    is_reactive = False
                if tree[i][INDEX_NODE_TYPE] == self.node_condition:
                    node_type = macro_node_reactive_condition if is_reactive else macro_node_condition
                    self.nodes_path.append([index, node_type, tree[value[0]][INDEX_NODE_FUNCTION], tree[value[1]][INDEX_NODE_FUNCTION], 
                                            tree[i][INDEX_NODE_FUNCTION]])
                elif tree[i][INDEX_NODE_TYPE] == self.node_action:
                    node_type = macro_node_reactive_action if is_reactive else macro_node_action
                    self.nodes_path.append([index, node_type, tree[value[0]][INDEX_NODE_FUNCTION], tree[value[1]][INDEX_NODE_FUNCTION], 
                                            tree[i][INDEX_NODE_FUNCTION]])
                elif tree[i][INDEX_NODE_TYPE] == self.node_retry_until_successful:
                    node_type = macro_node_reactive_retry_until_success if is_reactive else macro_node_retry_until_success
                    self.nodes_path.append([index, node_type, tree[value[0]][INDEX_NODE_FUNCTION], tree[value[1]][INDEX_NODE_FUNCTION], 
                                            index + 1, tree[i][INDEX_NODE_DECORATOR_NUM_ATTEMPTS], tree[i][INDEX_NODE_DECORATOR_POINTER]])
                index += 1

        for i in range(len(self.nodes_path)):
            succes_case = False
            fail_case = False
            for j in range(len(self.nodes_path)):
                if((self.nodes_path[i][INDEX_SUCCESS_CASE] == self.nodes_path[j][INDEX_POINTER_VERIFY]) and
                   (self.is_decorator_node(self.nodes_path[j][INDEX_NODE_TYPE]) or i < j)):
                    self.nodes_path[i][INDEX_SUCCESS_CASE] = self.nodes_path[j][0]
                    succes_case = True
                if((self.nodes_path[i][INDEX_FAIL_CASE] == self.nodes_path[j][INDEX_POINTER_VERIFY]) and
                   (self.is_decorator_node(self.nodes_path[j][INDEX_NODE_TYPE]) or i < j)):
                    self.nodes_path[i][INDEX_FAIL_CASE] = self.nodes_path[j][0]
                    fail_case = True
                if((succes_case) and (fail_case)):
                    break

        for i in self.nodes_path:
            print(i)
        return self.nodes_path