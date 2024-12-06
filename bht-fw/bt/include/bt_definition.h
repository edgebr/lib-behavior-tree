/**
 * @file bt_definition.h
 * @author Renilson Almeida (renilson.123@hotmail.com)
 * @brief Header of behavior tree definitions.
 * @version 1.0
 * @date 26/06/24
 *
 * @copyright Copyright (c) 2024 Renilson Almeida
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#ifndef BT_DEFINITION_H_
#define BT_DEFINITION_H_

#include <stdint.h>

/**
 * @brief Non-existing item.
 * Last ID of 32-bit value.
 *
 */
#define BT_DEFINITION_TREE_UNRELATED 0xFFFFFFFF

/**
 * @brief Error checking a function of type bt_definition_status_t.
 *
 */
#define BT_DEFINITION_TREE_STATUS(_err)       \
    do                                        \
    {                                         \
        if (_err)                             \
        {                                     \
            return BT_DEFINITION_STATUS_FAIL; \
        }                                     \
        return BT_DEFINITION_STATUS_SUCCESS;  \
    } while (0)

/**
 * @brief Enumerates the types of tree returns.
 *
 */
typedef enum
{
    BT_DEFINITION_STATUS_SUCCESS = 0, /**< Status success in node or tree. */
    BT_DEFINITION_STATUS_FAIL,        /**< Status failed in node or tree. */
    BT_DEFINITION_STATUS_RUNNING,     /**< Status running in node or tree. */
    BT_DEFINITION_STATUS_ERROR,       /**< Status error in node or tree. */
    __BT_DEFINITION_STATUS_AMOUNT,    /**< Status amount in lib. */
} bt_definition_status_t;

/**
 * @brief Enumerates the types of nodes in the tree.
 *
 */
typedef enum
{
    BT_DEFINITION_NODE_CONDITION = 0,  /**< Type of interation condition node. */
    BT_DEFINITION_NODE_ACTION,         /**< Type of interation action node. */
    BT_DEFINITION_NODE_ACTION_TIMEOUT, /**< Type of interation action timeout node. */
    __BT_DEFINITION_NODE_AMOUNT,       /**< Amount of nodes. */
} bt_definition_node_type_t;

/**
 * @brief Data loaded into an interaction type node containing function.
 *
 */
typedef struct bt_definition_interation_funtion
{
    union
    {
        int (*function)(void); /**< Pointer to interaction function. */
        uint32_t timeout_ms;   /**< Delay timeout value for interation action node delay. */
    };
} bt_definition_interation_funtion_t;

/**
 * @brief Data loaded into a condition interation node.
 *
 */
typedef struct bt_definition_interation_condition
{
    uint32_t st_condition_index; /**< Index to next struture condition if have success. */
    uint32_t ft_condition_index; /**< Index to next struture condition if have fail. */
} bt_definition_interation_condition_t;

/**
 * @brief Data loaded into interation condition node.
 *
 */
typedef struct bt_definition_node_interation
{
    uint32_t st_index;                             /**< Index to next struture if have success. */
    uint32_t ft_index;                             /**< Index to next struture if have fail. */
    bt_definition_interation_funtion_t interation; /**< Data of interation. */
    union
    {
        bt_definition_interation_condition_t condition; /**< indexes of conditions structs already executed. */
    };
} bt_definition_node_interation_t;

/**
 * @brief Structure of a tree node.
 *
 */
typedef struct bt_definition_node
{
    bt_definition_node_type_t node_type; /**< Node type. */
    union
    {
        bt_definition_node_interation_t interation_node;
    };
} bt_definition_node_t;

/**
 * @brief Estrutura de itens pertinentes de uma árvore.
 *
 */
typedef struct bt_definition_tree_data
{
    bt_definition_status_t last_node_state; /**< State of tree execution. */
    uint32_t node_index;                    /**< Node to be executed. */
    uint32_t condition_index;               /**< Node condition to be executed. */
    bt_definition_node_t *tree;             /**< Tree. */
} bt_definition_tree_data_t;

/**
 * @brief Macro that creates condition node condition.
 *
 */
#define BT_DEFINITION_CREATE_NODE_CONDITION(_function, _success_target, _fail_target) \
    {                                                                                 \
        .node_type = BT_DEFINITION_NODE_CONDITION,                                    \
        .interation_node.interation.function = _function,                             \
        .interation_node.success_target_index = _success_target,                      \
        .interation_node.fail_target_index = _fail_target,                            \
    }

/**
 * @brief Macro that creates action node common.
 *
 */
#define BT_DEFINITION_CREATE_NODE_ACTION(_function, _success_target, _fail_target) \
    {                                                                              \
        .node_type = BT_DEFINITION_NODE_ACTION,                                    \
        .interation_node.interation.function = _function,                          \
        .interation_node.st_index = _success_target,                               \
        .interation_node.ft_index = _fail_target,                                  \
    }

/**
 * @brief Macro that creates delay action node with delay.
 *
 */
#define BT_DEFINITION_CREATE_NODE_ACTION_DELAY(_timeout_ms, _sibling, _parent) \
    {                                                                          \
        .node_type = BT_DEFINITION_NODE_ACTION,                                \
        .interation_node.interation.timeout_ms = _timeout_ms,                  \
        .interation_node.st_index = _sibling,                                  \
        .interation_node.ft_index = _parent,                                   \
    }

#endif /* BT_DEFINITION_H_ */