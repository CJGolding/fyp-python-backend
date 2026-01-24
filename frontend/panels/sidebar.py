import streamlit as st

from common.types import InsertionInputField, GameManager
from frontend.components import system_controls, animation_controls, player_insertion
from frontend.state import get_state, StateKeys, set_state

_INSERTION_MODES: list[str] = ["Manual", "Automatic"]

_MANUAL_INSERTION_FIELDS: dict[str, InsertionInputField] = {
    "player_skill": ("Skill", 0, 5000, 1500)
}

_AUTOMATIC_INSERTION_FIELDS: dict[str, InsertionInputField] = {
    "num_players": ("Count", 1, 100, 10),
    "mean": ("Mean", 0, 5000, 1500),
    "std_dev": ("Std Dev", 0, 1000, 200)
}


def _render_insertion_controls(game_manager: GameManager, controls_disabled: bool) -> None:
    """
    Render the player insertion controls in the sidebar, allowing selection between manual and automatic modes.
    :param game_manager: The game manager instance to interact with.
    :param controls_disabled: Whether the controls should be disabled.
    """
    st.header("Player Insertion")
    col1, col2 = st.columns([2, 3])
    col1.text("Insertion Mode")
    insertion_mode: str = col2.selectbox("Insertion Mode", _INSERTION_MODES, disabled=controls_disabled,
                                         label_visibility="collapsed", index=get_state(StateKeys.INSERTION_MODE))
    set_state(StateKeys.INSERTION_MODE, _INSERTION_MODES.index(insertion_mode))
    if insertion_mode == "Manual":
        player_insertion.render(controls_disabled, _MANUAL_INSERTION_FIELDS, game_manager.insert_player_manually_async,
                                "Insert Player")
    else:
        player_insertion.render(controls_disabled, _AUTOMATIC_INSERTION_FIELDS,
                                game_manager.insert_players_automatically_async, "Insert Players")


def render(game_manager: GameManager, total_steps: int, current_index: int, is_executing_async: bool, is_playing: bool,
           is_on_final_step: bool, has_stopped: bool) -> None:
    """
    Render the sidebar panel with system controls, animation controls, and player insertion controls.
    :param game_manager: The game manager instance to interact with.
    :param total_steps: The total number of steps in the simulation.
    :param current_index: The current step index in the simulation.
    :param is_executing_async: Whether an asynchronous operation is currently executing.
    :param is_playing: Whether the animation is currently playing.
    :param is_on_final_step: Whether the simulation is on the final step.
    :param has_stopped: Whether the system has been stopped.
    """
    with st.sidebar:
        system_controls.render(game_manager, (not is_on_final_step) or is_executing_async, has_stopped)

        animation_controls.render(current_index, total_steps - 1, is_playing, is_executing_async, is_on_final_step,
                                  has_stopped)

        _render_insertion_controls(game_manager, (not is_on_final_step) or is_executing_async or has_stopped)
