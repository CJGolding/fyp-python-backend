import streamlit as st

from common.types import GameManager
from frontend.state import reset_all, start_playback, stop_execution


def render(game_manager: GameManager, controls_disabled: bool, has_stopped: bool) -> None:
    """
    Render system control buttons for stopping, resetting, and creating matches.
    :param game_manager: The game manager instance to interact with.
    :param controls_disabled: Whether the controls should be disabled.
    :param has_stopped: Whether the system has been stopped.
    """
    st.header("System Controls")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Stop", width='stretch', disabled=has_stopped or game_manager.is_executing_async):
            stop_execution()
            st.rerun()
    with col2:
        if st.button("Reset", width='stretch'):
            reset_all()
            st.rerun()
    if st.button("Create Match", type="primary", width='stretch', disabled=controls_disabled or has_stopped):
        game_manager.create_match_async()
        start_playback()
        st.rerun()

    st.divider()
