"""
Streamlit Matchmaking Visualiser
A visualisation tool for matchmaking algorithms with step-by-step animation.
This is the main application file that sets up the Streamlit interface, manages state, and coordinates rendering of different panels.
"""
import logging
import sys
import time

import streamlit as st

from common.types import Step, GameManager
from frontend.panels import (
    sidebar,
    simulation,
    configuration,
    statistics
)
from frontend.state import init_session_state, get_state, set_state, StateKeys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

LOG: logging.Logger = logging.getLogger(__name__)
_ANIMATION_DELAY: float = 1.0
_POLL_INTERVAL: float = 0.25

st.set_page_config(page_title="Matchmaking Visualiser", layout="wide")
st.title("Matchmaking System Visualiser")

init_session_state()

if not get_state(StateKeys.INITIALISED):
    configuration.render()
else:
    # Gather relevant state variables for rendering
    game_manager: GameManager = get_state(StateKeys.GAME_MANAGER)
    steps: list[Step] = game_manager.recorder.steps
    total_steps: int = len(steps)
    current_index: int = get_state(StateKeys.CURRENT_STEP)
    is_on_final_step: bool = current_index >= total_steps - 1
    is_executing_async: bool = game_manager.is_executing_async
    is_playing: bool = get_state(StateKeys.IS_PLAYING)
    is_time_sensitive: bool = get_state(StateKeys.IS_TIME_SENSITIVE)
    has_stopped: bool = get_state(StateKeys.STOPPED)
    step: Step = steps[current_index] if steps else None

    # Render separated panels
    sidebar.render(game_manager, total_steps, current_index, is_executing_async, is_playing, is_on_final_step,
                   has_stopped)

    if has_stopped:
        statistics.render(game_manager, is_time_sensitive)
    simulation.render(steps, step, current_index, is_executing_async, is_on_final_step, is_time_sensitive)

    # Auto-advance animation or poll for new steps during async execution
    if is_executing_async or is_playing:
        if is_playing and not is_on_final_step:
            time.sleep(_ANIMATION_DELAY)
            set_state(StateKeys.CURRENT_STEP, current_index + 1)
        elif is_executing_async:
            time.sleep(_POLL_INTERVAL)
        elif is_on_final_step:
            set_state(StateKeys.IS_PLAYING, False)
        st.rerun()
