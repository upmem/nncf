"""
 Copyright (c) 2022 Intel Corporation
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
from typing import Optional
from typing import List

import torch

from nncf.common.graph import NNCFGraph
from nncf.common.graph import NNCFNodeName
from nncf.torch.graph.graph import NNCFNode
from nncf.torch.tensor import PTNNCFTensor
from nncf.torch.nncf_network import NNCFNetwork


def get_bn_node_for_conv(graph: NNCFGraph, conv_node: NNCFNode) -> Optional[NNCFNode]:
    successors = graph.get_next_nodes(conv_node)
    for succ in successors:
        if succ.node_type == 'batch_norm':
            return succ
    return None


def get_bn_for_conv_node_by_name(target_model: NNCFNetwork, conv_node_name: NNCFNodeName) -> Optional[torch.nn.Module]:
    """
    Returns a batch norm module in target_model that corresponds immediately following a given
    convolution node in the model's NNCFGraph representation.
    :param target_model: NNCFNetwork to work with
    :param module_scope:
    :return: batch norm module
    """
    graph = target_model.get_original_graph()
    conv_node = graph.get_node_by_name(conv_node_name)
    bn_node = get_bn_node_for_conv(graph, conv_node)
    if bn_node is None:
        return None
    bn_module = target_model.get_containing_module(bn_node.node_name)
    return bn_module


def init_output_masks_in_graph(graph: NNCFGraph, nodes: List):
    """
    Initialize masks in graph for mask propagation algorithm

    :param graph: NNCFNetwork
    :param nodes: list with pruned nodes
    """
    for node in graph.get_all_nodes():
        node.data.pop('output_mask', None)

    for minfo in nodes:
        mask = minfo.operand.binary_filter_pruning_mask
        nncf_node = graph.get_node_by_id(minfo.nncf_node_id)
        nncf_node.data['output_mask'] = PTNNCFTensor(mask)
