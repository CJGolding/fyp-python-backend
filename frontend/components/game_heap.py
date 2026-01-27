import streamlit as st
from graphviz import Digraph

from backend.step import Step
from common.actions import HeapActions
from common.types import RecordedState, HeapSnapshot
from frontend.components._helpers import (
    render_legend,
    render_empty_graph,
    Colours,
    LegendItem
)

_HEAP_LEGEND: list[LegendItem] = [
    ("Root", Colours.ROOT, Colours.TEXT_DARK),
    ("Node", Colours.NODE, Colours.TEXT_DARK),
    ("New", Colours.NEW_NODE, Colours.TEXT_DARK),
    ("Removed", Colours.REMOVED_NODE, Colours.TEXT_DARK),
    ("Created Match", Colours.MATCH_NODE, Colours.TEXT_DARK)
]


def _get_node_fill_colour(index: int, target_index: int, action: HeapActions) -> Colours:
    """
    Determine fill colour for a heap node.
    :param index: The index of the current node.
    :param target_index: The index of the target node being acted upon.
    :param action: The action being performed on the current step.
    :return: The fill colour for the node.
    """
    if target_index == index:
        if action == HeapActions.REMOVE: return Colours.REMOVED_NODE
        if action == HeapActions.INSERT: return Colours.NEW_NODE
        if action == HeapActions.CREATE: return Colours.MATCH_NODE
    if index == 0: return Colours.ROOT
    return Colours.NODE


def render(step: Step, is_on_final_step: bool, is_time_sensitive: bool) -> None:
    """
    Render heap as binary tree visualisation.
    :param step: The current simulation step containing the heap snapshot.
    :param is_on_final_step: Whether the simulation is on the final step.
    :param is_time_sensitive: Whether to include time-sensitive information in the node labels.
    """
    heap_size: int = len(step.heap_snapshot.state) if step and step.heap_snapshot and step.heap_snapshot.state else 0
    st.subheader(f"Candidate Games Heap ({heap_size} games)")
    render_legend(_HEAP_LEGEND)

    if not step or not step.heap_snapshot or not step.heap_snapshot.state:
        render_empty_graph('Candidate Games Heap', shape='circle')
        return

    heap_snapshot: HeapSnapshot = step.heap_snapshot
    heap_state: RecordedState = heap_snapshot.state

    graph: Digraph = Digraph(comment='Candidate Games Heap')
    graph.attr(rankdir='TB', bgcolor='white', nodesep='0.1', ranksep='0.2', center='true')
    graph.attr('node', shape='circle', style='filled', fontname='Arial', fontsize='9',
               fixedsize='true', width='0.7', height='0.5', penwidth='1', color='black')

    target, action = (heap_snapshot.target_game, heap_snapshot.action) if not is_on_final_step else (None, None)

    for i, item in enumerate(heap_state):
        metric_key: str = "g" if is_time_sensitive else "f"
        metric_val: float = item.get("priority") or item.get("imbalance", 0)
        fill: Colours = _get_node_fill_colour(i, target, action)

        graph.node(f'h_{i}', f"{metric_key}={metric_val:.1f}\nP{item.get('anchor_player_id')}", fillcolor=fill.value)

        for child in (2 * i + 1, 2 * i + 2):
            if child < len(heap_state):
                graph.edge(f'h_{i}', f'h_{child}', color='#666666')

    st.graphviz_chart(graph)
