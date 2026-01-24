import streamlit as st

from frontend.components import configuration_form, configuration_info


def render() -> None:
    col1, col2 = st.columns(2)

    with col1:
        configuration_form.render()

    with col2:
        configuration_info.render()
