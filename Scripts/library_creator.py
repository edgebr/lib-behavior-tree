import os
from datetime import date

class ARCHIVE_CREATOR:
    def __init__(self):
        self.text = ""
        self.name = ""
        self.email = ""
        self.version = ""
        self.copyrights = ""
        self.output_file = "Output Files"

    def get_output_folder(self):
        return self.output_file

    def set_text(self, name = None, email = None, version = None, copyrights = None):
        self.name = name if name != None else ""
        self.email = email if email != None else ""
        self.version = version if version != None else ""
        self.copyrights = copyrights if copyrights != None else ""

    def tree_header(self, archive):
        value          = "behavior tree" if archive != "attempts" else archive
        today          = date.today()
        init           = "/**\n"
        file_name      = f" * @file bt_{(archive.lower())}.h\n"
        author         = f" * @author {self.name} ({self.email.lower()})\n"
        brief          = f" * @brief Header of {value} {archive.lower()}.\n"
        version        = f" * @version {self.version}\n" if (self.version != None) else ""
        date_generated = f' * @date {today.strftime("%d/%m/%Y")}\n'
        copyright      = f" *\n * @copyright Copyright © {today.year} {self.copyrights}. Todos os direitos reservados.\n"
        end            = " *\n */\n\n"
        self.text      = init + file_name + author + brief + version + date_generated + copyright + end

    def tree_top(self, archive, variables=False):
        ifndef             = f"#ifndef INCLUDE_BTREE_{archive.upper()}_H_\n"
        define             = f"#define INCLUDE_BTREE_{archive.upper()}_H_\n"    
        include            = "\n#include \"bt_definition.h\"\n" if variables else ""
        self.text         += ifndef + define + include + "\n"

    def tree_vector(self, archive, bt_array):
        self.text += "/**\n"
        self.text += f" * @brief Array nodes of behavior tree {(archive.lower())}.\n"
        self.text += " *\n */\n"
        self.text += f"const tc_bt_definition_t* BT_TREE_{(archive.upper())} [] = \n"
        self.text += "{\n"
        for item in bt_array:
            index = item[0]
            node_type = item[1]
            params = ', '.join(map(str, item[2:]))
            self.text += f"         [{index}] = {node_type}({params}), \\\n"
        self.text += "}\n\n"

    def tree_variables(self, max_ramification_attempts, id):
        init_comment       = "\n/**\n"
        define_brief       = " * @brief Maximum number of attempts boxes in a ramification.\n"
        end_comment        = " *\n */\n"
        define             = f"#define BT_VARIABLES_MAX_ATTEMPT_RAMIFICATION {max_ramification_attempts}\n"
        tree_pointer_brief = init_comment + f" * @brief Pointer to behavior tree {(id.lower())}.\n" + end_comment
        tree_pointer       = f"tc_bt_definition_t *bt_variables_{(id.lower())};\n"
        tree_index_pointer = init_comment + f" * @brief Index of behavior tree {(id.lower())}.\n" + end_comment
        tree_index         = f"uint8_t bt_variables_{(id.lower())}_index;\n"
        array_brief        = " * @brief Stores attempt variables.\n"
        array              = "uint8_t bt_variables_values[BT_VARIABLES_MAX_ATTEMPT_RAMIFICATION];\n\n"
        if max_ramification_attempts > 0:
            self.text         += init_comment + define_brief + end_comment + define
        self.text         += tree_pointer_brief + tree_pointer
        self.text         += tree_index_pointer + tree_index
        if max_ramification_attempts > 0:
            self.text     +=  init_comment + array_brief + end_comment + array

    def tree_end(self, archive):
        endif      = f"#endif /* INCLUDE_BTREE_{archive.upper()}_H_ */"
        self.text += endif
        os.makedirs(self.output_file, exist_ok=True)
        output_file = os.path.join(self.output_file, f'bt_{archive}.h')
        with open(output_file, 'w') as file:
            file.write(self.text)
        self.text = ""

    def generate_tree(self, archive, nodes):
        self.tree_header(archive)
        self.tree_top(archive)
        self.tree_vector(archive, nodes)
        self.tree_end(archive)

    def generate_variables(self, num_max_attempts, id):
        self.tree_header("variables")
        self.tree_top("variables", variables=True)
        self.tree_variables(num_max_attempts, id)
        self.tree_end("variables")