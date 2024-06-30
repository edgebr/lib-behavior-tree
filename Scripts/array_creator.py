import os
import xml.etree.ElementTree as ET
from library_creator import ARCHIVE_CREATOR

node_index_invalid = 'TC_BT_PROCESS_TREE_UNRELATED'
node_fallback = 'Fallback'
node_sequence = 'Sequence'
node_action = 'Script'
node_condition = 'ScriptCondition'
node_decorator_attempts = 'RetryUntilSuccessful'
node_delay = 'Sleep'
node_subtree = 'Subtree'
macro_node_root = 'TC_BT_PROCESS_CREATE_NODE_ROOT'
macro_node_fallback = 'TC_BT_PROCESS_CREATE_NODE_FALLBACK'
macro_node_sequence = 'TC_BT_PROCESS_CREATE_NODE_SEQUENCE'
macro_node_action = 'TC_BT_PROCESS_CREATE_NODE_ACTION'
macro_node_condition = 'TC_BT_PROCESS_CREATE_NODE_CONDITION'
macro_node_decorator_attempts = 'TC_BT_PROCESS_CREATE_NODE_ATTEMPTS'
macro_node_delay = 'TC_BT_DEFINITION_CREATE_NODE_ACTION_DELAY'
macro_node_subtree = 'TC_BT_PROCESS_CREATE_NODE_SUBTREE'

class BT_ARRAY:
    def __init__(self):
        self.node_number = 0
        self.attempts_nodes_ramification = 0
        self.max_attempts_nodes = 0
        self.tree = []
        self.folder = ""
        self.library = ARCHIVE_CREATOR()

    def get_max_attempts(self):
        return self.max_attempts_nodes
    
    def set_attempts(self, attempts):
        self.max_attempts_nodes = attempts
        self.attempts_nodes_ramification = attempts

    def set_archive_data(self, name = None, email = None, version = None, copyrights = None):
        self.library.set_text(name, email, version, copyrights)

    def set_children(self):
        if(self.node_number == 0):
            return

        node_type = self.tree[-1][1]

        if macro_node_root == node_type or macro_node_fallback == node_type or macro_node_sequence == node_type or \
           macro_node_decorator_attempts == node_type:
            self.tree[-1][2] = self.node_number

    def set_sibling(self):
        for i in range(1, len(self.tree)):
            sibling_index = 0
            parent_index = self.tree[i][0]
            for j in range(len(self.tree) - 1, i, -1):
                if parent_index == self.tree[j][-1]:
                    self.tree[j][-2] = sibling_index
                    sibling_index = self.tree[j][0]

    def mount_nodes(self, element, node_parent_number):
        self.node_number += 1

        is_decoration_attempts = False

        if node_fallback == element.tag:
            node = [self.node_number, macro_node_fallback, 0, 0, node_parent_number]
            node_parent_number = self.node_number
        elif node_sequence == element.tag:
            node = [self.node_number, macro_node_sequence, 0, 0, node_parent_number]
            node_parent_number = self.node_number
        elif node_action == element.tag:
            node = [self.node_number, macro_node_action, "&" + element.get('code'), 0, node_parent_number]
            node_parent_number -= 1
        elif node_condition == element.tag:
            node = [self.node_number, macro_node_condition, "&" + element.get('code'), 0, node_parent_number]
            node_parent_number -= 1
        elif node_decorator_attempts == element.tag:
            node = [self.node_number, macro_node_decorator_attempts, 0, element.get('num_attempts'), f'&bt_attempts[{self.attempts_nodes_ramification}]', 0,  node_parent_number]
            node_parent_number = self.node_number
            self.attempts_nodes_ramification += 1
            is_decoration_attempts = True
            if self.attempts_nodes_ramification > self.max_attempts_nodes:
                self.max_attempts_nodes = self.attempts_nodes_ramification
        elif node_delay == element.tag:
            node = [self.node_number, macro_node_delay, element.get('msec'), 0,  node_parent_number]
            node_parent_number = self.node_number
        elif node_subtree == element.tag:
            node = [self.node_number, macro_node_subtree, element.get('subtree'), 0,  node_parent_number]
            node_parent_number = self.node_number
            subtree = BT_ARRAY()
            subtree.set_archive_data(self.library.name, self.library.email, self.library.version, self.library.copyrights)
            subtree.set_attempts(self.attempts_nodes_ramification)
            subtree.process_tree(self.folder, element.get('subtree'))
            self.attempts_nodes_ramification = subtree.get_max_attempts()
        else:
            self.node_number = 0
            node = [self.node_number, macro_node_root, node_parent_number]

        self.set_children()
        self.tree.append(node)

        for child in element:
            self.mount_nodes(child, node_parent_number)

        if is_decoration_attempts:
            self.attempts_nodes_ramification -= 1

    def open_xml(self, archive, id = None):
        tree = ET.parse(archive)
        root = tree.getroot()
        for behavior_tree in root.findall('BehaviorTree'):
            tree_id = behavior_tree.get('ID')
            file_name = f"{self.library.get_output_folder()}/bt_{tree_id}.h"
            if (id == None or id == tree_id) and not os.path.isfile(file_name):
                self.mount_nodes(behavior_tree, 0)
                self.set_sibling()
                self.library.generate_tree(tree_id, self.tree)
                self.tree.clear()

    def load_archives(self, id = None):
        trees = os.listdir(self.folder)
        for archive in trees:
            self.open_xml(f"{self.folder}/{archive}", id)

    def process_tree(self, folder, id):
        self.folder = folder
        self.load_archives(id)

    def create_trees(self, folder, id):
        self.folder = folder
        self.load_archives()
        self.library.generate_variables(self.max_attempts_nodes, id)
        self.max_attempts_nodes = 0