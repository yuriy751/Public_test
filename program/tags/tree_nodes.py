from dataclasses import dataclass


@dataclass(frozen=True)
class NodeState:
    method_tree_node: str = 'Method tree node'