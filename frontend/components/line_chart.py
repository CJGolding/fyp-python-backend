import altair as alt
import streamlit as st
from pandas import DataFrame


def render(data: list, x_label: str, y_label: str) -> None:
    """
    Render a line chart of a given recorded statistic or info message if no data.
    :param data: The recorded statistic data points.
    :param x_label: The label for the x-axis.
    :param y_label: The label for the y-axis.
    """
    if data:
        df: DataFrame = DataFrame({"Step": range(len(data)), y_label: data})
        chart: alt.Chart = alt.Chart(df).mark_line().encode(
            x=alt.X("Step:Q", title=x_label),
            y=alt.Y(f"{y_label}:Q", title=y_label)
        ).properties(height=300).configure_view(strokeWidth=0)
        st.altair_chart(chart, width='stretch')
    else:
        st.info("No data recorded yet")
