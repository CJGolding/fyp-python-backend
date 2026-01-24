import streamlit as st


def render() -> None:
    """Render key information about the application and its configuration."""
    st.subheader("Application Overview")
    st.markdown("""
    This application simulates a game matchmaking system with configurable parameters.
    You can choose between two modes: 

    **Configuration Parameters:**
    - **Mode:** Unrestricted or Time-Sensitive.
    - **GameTeam Size (k):** Number of players per team (1-5).
    - **Fairness Norm (p):** Norm used to measure fairness (≥1.0).
    - **Uniformity Norm (q):** Norm used to measure uniformity (≥1.0).
    - **Fairness Weight (α):** Weight given to fairness in matchmaking (>0.0).
    - **Queue Weight (β):** Weight given to queue time in Time-Sensitive mode (>0.0).
    - **Matchmaking Approach:** Option to use the heuristic of reducing the skill window to 2k-1 for faster matchmaking.

    Use the configuration panel to set these parameters and initialise the game manager.
    """)
