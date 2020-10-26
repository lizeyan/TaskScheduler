import os
from typing import TypeVar, Iterable, Tuple, Set, Union, FrozenSet, MutableSet

from ordered_set import OrderedSet

from .tasks import Task


class DAG(object):
    T = TypeVar('T')
    Edge = Tuple[T, T]
    SetLike = Union[OrderedSet[T], Set[T], FrozenSet[T], MutableSet[T]]

    class NotDAGError(RuntimeError):
        pass

    def __init__(self, nodes: Iterable[T], edges: Iterable[Edge], T=Task):
        self.T = T
        self._nodes = OrderedSet(nodes)
        self._edges = OrderedSet(edges)
        if not self._is_acyclic():
            raise self.NotDAGError(f"Graph is not DAG: {self}")

    def remove_node(self, node: T) -> "DAG":
        return DAG(
            self._nodes - {node},
            OrderedSet(filter(lambda e: e[0] != node and e[1] != node, self._edges))
        )

    def remove_nodes(self, nodes: Iterable[T]) -> "DAG":
        nodes = OrderedSet(nodes)
        return DAG(
            self._nodes - nodes,
            OrderedSet(filter(lambda e: (e[0] not in nodes) and (e[1] not in nodes), self._edges))
        )

    @property
    def nodes(self) -> OrderedSet[T]:
        return self._nodes

    @property
    def edges(self) -> OrderedSet[Edge]:
        return self._edges

    @property
    def source(self):
        return next(iter(filter(lambda v: len(self.in_edges(v)) == 0, self._nodes)))

    @property
    def sink(self):
        return next(iter(filter(lambda v: len(self.out_edges(v)) == 0, self._nodes)))

    def in_edges(self, node: T) -> OrderedSet[Edge]:
        return OrderedSet(filter(lambda edge: edge[1] == node, self._edges))

    def out_edges(self, node: T) -> OrderedSet[Edge]:
        return OrderedSet(filter(lambda edge: edge[0] == node, self._edges))

    def _is_acyclic(self) -> bool:
        # TODO: optimize
        left = self._nodes
        while len(left) > 0:
            visited = OrderedSet()
            no_out_edges = list(filter(lambda v: len(self.out_edges(v)) == 0, left))
            if len(no_out_edges) <= 0:
                return False
            no_cycle = self.__dfs(no_out_edges[0], visited)
            if not no_cycle:
                return False
            left = left - visited
        return True

    def dependency_subgraph(self, node: T) -> "DAG":
        visited = OrderedSet()
        self.__dfs(node, visited, forward=True)
        return self.remove_nodes(self.nodes - visited)

    def __str__(self):
        return f"nodes: {','.join(str(_) for _ in self._nodes)} edges: {','.join(str(_) for _ in self._edges)}"

    def __repr__(self):
        return str(self)

    def __dfs(self, node: T, visited: SetLike, path: SetLike = None, forward=False) -> bool:
        if path is None:
            path = OrderedSet()
        visited.add(node)
        no_circle = True
        for u, v in self.in_edges(node) if not forward else self.out_edges(node):
            next_one = v if forward else u
            if next_one in path:
                no_circle = False
                continue
            if next_one in visited:
                continue
            no_circle = no_circle and self.__dfs(next_one, visited, path=path | {node}, forward=forward)
        return no_circle

    def __eq__(self, other):
        if not isinstance(other, DAG):
            return False
        return set(self.nodes) == set(other.nodes) and set(self.edges) == set(other.edges)

    def __hash__(self):
        return hash(frozenset(self.nodes) | frozenset(self.edges))

    def format_subtree(self, node: T = None) -> str:

        return os.linesep.join(
            [f'{node}'] +
            self.format_add_bar([self.__indent_formatted(self.format_subtree(v)) for u, v in self.out_edges(node)])
        )

    def format_tree(self) -> str:
        ret = os.linesep.join(
            self.format_add_bar([
                self.__indent_formatted(self.format_subtree(_)) for _ in self.nodes if len(self.in_edges(_)) == 0
            ])
        )

        return ret

    @staticmethod
    def __indent_formatted(content, level=1):
        data = content.splitlines()
        ret = list(map(
            lambda item:
            f""
            f"{(' ' if item[0] != 0 else '─') * level * 2}"
            f" {item[1]}",
            enumerate(data)
        ))
        return os.linesep.join(ret)

    @staticmethod
    def format_add_bar(lines):
        lines = sum([_.splitlines() for _ in lines], [])
        seq_indices = [idx for idx, line in enumerate(lines) if line[0] == '─']
        if len(seq_indices) <= 0:
            return lines
        first_sep, last_sep = seq_indices[0], seq_indices[-1]
        ret = []
        for idx, line in enumerate(lines):
            if first_sep <= idx < last_sep:
                adder = '├' if line[0] == '─' else '│'
            elif idx == last_sep:
                adder = '└'
            else:
                adder = ' '
            ret.append(f"{adder}{line}")
        return ret
