import streamlit as st
from graphviz import Digraph

from common.actions import QueueActions
from common.types import RecordedState, QueueSnapshot, Step, NodeColours
from frontend.components._helpers import (
    render_legend,
    render_empty_graph,
    render_player_node,
    Colours,
    LegendItem, render_horizontal_rank
)

_NODES_PER_ROW: int = 14
_QUEUE_LEGEND: list[LegendItem] = [
    ("Default", Colours.DEFAULT, Colours.TEXT_DARK),
    ("Window", Colours.WINDOW, Colours.TEXT_DARK),
    ("Anchor", Colours.ANCHOR, Colours.TEXT_DARK),
    ("Team X", Colours.TEAM_X, Colours.TEXT_LIGHT),
    ("Team Y", Colours.TEAM_Y, Colours.TEXT_DARK),
    ("Added", Colours.INSERTED, Colours.TEXT_DARK),
    ("Removed", Colours.REMOVED, Colours.TEXT_DARK),
]


def _get_player_colour(idx: int, target_idx: int, action: QueueActions, team_x: set, team_y: set,
                       window: set) -> NodeColours:
    """
    Determine fill and font colour for a player node.
    :param idx: The index of the player in the queue.
    :param target_idx: The index of the target / anchor player being acted upon.
    :param action: The action being performed on the current step.
    :param team_x: Set of indices belonging to Team X.
    :param team_y: Set of indices belonging to Team Y.
    :param window: Set of indices currently in the window.
    :return: A tuple containing the fill colour and font colour.
    """
    if idx in team_x: return Colours.TEAM_X, Colours.TEXT_LIGHT
    if idx in team_y: return Colours.TEAM_Y, Colours.TEXT_DARK
    if idx in window: return Colours.WINDOW, Colours.TEXT_DARK
    if target_idx == idx:
        if action == QueueActions.INSERT: return Colours.INSERTED, Colours.TEXT_DARK
        if action == QueueActions.REMOVE: return Colours.REMOVED, Colours.TEXT_DARK
        if action == QueueActions.ANCHOR: return Colours.ANCHOR, Colours.TEXT_LIGHT
    return Colours.DEFAULT, Colours.TEXT_DARK


def render(step: Step, is_on_final_step: bool, is_time_sensitive: bool) -> None:
    """
    Render player queue as horizontal visualisation with wrapping over multiple rows to prevent nodes from being too small.
    :param step: The current simulation step containing the queue snapshot.
    :param is_on_final_step: Whether the simulation is on the final step.
    :param is_time_sensitive: Whether to include time-sensitive information in the node labels.
    """
    queue_length: int = len(
        step.queue_snapshot.state) if step and step.queue_snapshot and step.queue_snapshot.state else 0
    st.subheader(f"Player Queue ({queue_length} players)")
    render_legend(_QUEUE_LEGEND)

    if not step or not step.queue_snapshot or not step.queue_snapshot.state:
        render_empty_graph('Player Queue', 'box')
        return

    queue_snapshot: QueueSnapshot = step.queue_snapshot
    players: RecordedState = queue_snapshot.state

    graph: Digraph = Digraph(comment='Player Queue')
    graph.attr(rankdir='TB', bgcolor='white', nodesep='0.08', ranksep='0.25')
    graph.attr('node', shape='box', style='filled,rounded', fontname='Arial', fontsize='9',
               fixedsize='true', width='0.7', height='0.5', penwidth='1', color='black')

    window, team_x, team_y, target, action = set(), set(), set(), None, None
    if not is_on_final_step and queue_snapshot:
        if queue_snapshot.window:
            window = queue_snapshot.window
        team_x: set[int] = queue_snapshot.team_x or set()
        team_y: set[int] = queue_snapshot.team_y or set()
        target, action = queue_snapshot.target_player, queue_snapshot.action

    for i, p in enumerate(players):
        fill_colour, font_colour = _get_player_colour(i, target, action, team_x, team_y, window)
        render_player_node(graph, f'p_{i}', p, fill_colour, font_colour, is_time_sensitive)

    num_rows: int = (len(players) + _NODES_PER_ROW - 1) // _NODES_PER_ROW
    for row in range(num_rows):
        start, end = row * _NODES_PER_ROW, min((row + 1) * _NODES_PER_ROW, len(players))
        row_nodes: list[str] = [f'p_{i}' for i in range(start, end)]
        render_horizontal_rank(graph, row_nodes)
        if row > 0:
            graph.edge(f'p_{(row - 1) * _NODES_PER_ROW}', f'p_{start}', style='invis')

    st.graphviz_chart(graph)
