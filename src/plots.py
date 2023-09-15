import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


NO_PLOT = "No plot"
BAR_TYPE = "Bar plot"
SCATTER_TYPE = "Scatter plot"
LINE_TYPE = "Line plot"
PIE_TYPE = "Pie chart"


def get_axis(df: pd.DataFrame) -> tuple:
    return df.columns[0], df.columns[1]


def format_int_pie_value(values):
    def _format_int_pie_value(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{v:,}'.format(v=val)
    return _format_int_pie_value


def plot_bar(data: pd.DataFrame) -> dict:
    x_axis, y_axis = get_axis(data)
    st.write("Bar plot:")
    fig, ax = plt.subplots()
    sns.barplot(x=data[x_axis], y=data[y_axis], ax=ax)
    st.pyplot(fig)

    return {"type": BAR_TYPE}


def plot_scatter(data: pd.DataFrame) -> dict:
    x_axis, y_axis = get_axis(data)
    st.write("Scatter plot:")
    fig, ax = plt.subplots()
    sns.scatterplot(x=data[x_axis], y=data[y_axis], ax=ax)
    st.pyplot(fig)

    return {"type": SCATTER_TYPE}


def plot_line(data: pd.DataFrame) -> dict:
    x_axis, y_axis = get_axis(data)
    st.write("Line plot:")
    st.line_chart(data, x=x_axis, y=y_axis)

    return {"type": LINE_TYPE}


def plot_pie(data: pd.DataFrame) -> dict:
    x_axis, y_axis = get_axis(data)
    st.write("Pie chart:")
    fig, ax = plt.subplots()
    ax.pie(data[y_axis], labels=data[x_axis], autopct=format_int_pie_value(data[y_axis]))
    st.pyplot(fig)

    return {"type": PIE_TYPE}


def plot(data: pd.DataFrame, plot_type: str) -> dict:
    if plot_type == BAR_TYPE:
        return plot_bar(data)
    elif plot_type == SCATTER_TYPE:
        return plot_scatter(data)
    elif plot_type == LINE_TYPE:
        return plot_line(data)
    elif plot_type == PIE_TYPE:
        return plot_pie(data)
    else:
        raise ValueError(f"Unknown plot type: {plot_type}")
