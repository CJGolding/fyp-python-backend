import streamlit as st


def render() -> None:
    """Render key information about the application and its configuration."""
    st.subheader("Overview")
    st.markdown("""
    This application simulates a game matchmaking system with configurable parameters, allowing users to visualise how different settings impact the matchmaking process.

    **Configuration Parameters:**
    - **Mode:** Unrestricted or Time-Sensitive.
    - **Team Size (k):** Number of players per team (1-5).
    - **Fairness Norm (p):** Norm used to measure fairness (≥1.0).
    - **Uniformity Norm (q):** Norm used to measure uniformity (≥1.0).
    - **Fairness Weight (α):** Weight given to fairness in matchmaking (>0.0).
    - **Queue Weight (β):** Weight given to queue time in Time-Sensitive mode (>0.0).
    - **Matchmaking Approach:** Option to use an approximate greedy partitioning algorithm (ideal for larger team sizes).
    """)
    st.warning(
        "Warning: A timeout has been set for matchmaking operations to prevent long-running processes, this means that the optimal match may not always be found within the time limit.")
