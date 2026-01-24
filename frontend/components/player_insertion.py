from typing import Optional

import streamlit as st

from common.types import InsertionInputField, AsynchronousFunction
from frontend.state import start_playback


def render(controls_disabled: bool, input_fields: dict[str, InsertionInputField],
           insertion_method: AsynchronousFunction, button_label: str = "Insert") -> None:
    """
    Render player insertion controls with input fields and an insertion button, handling both manual and automatic modes.
    :param controls_disabled: Whether the controls should be disabled.
    :param input_fields: A dictionary mapping input field keys to their labels and number input parameters.
    :param insertion_method: The method to call for inserting a player.
    :param button_label: The label for the insertion button.
    """
    insertion_values: dict[str, Optional[int]] = {key: None for key in input_fields.keys()}
    for input_key, input_values in input_fields.items():
        col1, col2 = st.columns([2, 3])
        col1.text(input_values[0])
        insertion_values[input_key] = col2.number_input(*input_values, disabled=controls_disabled,
                                                        label_visibility="collapsed")
    if st.button(button_label, type="primary", disabled=controls_disabled, width='stretch'):
        insertion_method(**insertion_values)
        start_playback()
        st.rerun()
