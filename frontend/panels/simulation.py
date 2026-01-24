import streamlit as st

from common.types import Step
from frontend.components import player_queue, game_heap, created_matches, parameters, status_bar
from frontend.state import get_state, StateKeys


def render(steps: list, step: Step, current_index: int, is_executing_async: bool, is_on_final_step: bool,
           is_time_sensitive: bool) -> None:
    """
    Render the main simulation panel with status bar, parameters, player queue, game heap, and created matches.
    :param steps: List of recorded simulation steps.
    :param step: The current simulation step to display.
    :param current_index: The current step index being displayed.
    :param is_executing_async: Whether an asynchronous operation is currently executing.
    :param is_on_final_step: Whether the simulation is on the final step.
    :param is_time_sensitive: Whether to include time-sensitive information in the visualisations.
    """
    status_bar.render(steps, current_index, is_executing_async, is_on_final_step)
    col1, col2 = st.columns([1, 3])

    with col1:
        parameters.render(get_state(StateKeys.PARAMS))

    with col2:
        player_queue.render(step, is_on_final_step, is_time_sensitive)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        game_heap.render(step, is_on_final_step, is_time_sensitive)
    with col2:
        created_matches.render(step, is_time_sensitive)
