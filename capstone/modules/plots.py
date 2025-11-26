import streamlit as st
import plotly.express as px
import pandas as pd

def plot_accident_data(df):

 # ---- Fix ordering for month and weekday ----
    MONTH_ORDER = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    WEEKDAY_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

    if "month" in df.columns:
        df["month"] = pd.Categorical(df["month"], categories=MONTH_ORDER, ordered=True)

    if "weekday" in df.columns:
        df["weekday"] = pd.Categorical(df["weekday"], categories=WEEKDAY_ORDER, ordered=True)

    # ---- Breakdown options ----
    breakdown_options = [
        "month", "day", "hour", "weekday", "municipality"
    ]

    # ---- Metric options ----
    metric_options = {
        "Number of accidents": None,  # uses count
        "Minor injuries": "minor_injuries_30d",
        "Serious injuries": "serious_injuries_30d",
        "Fatalities": "fatalities_30d"
    }

    col1, col2, col3 = st.columns(3)

    # Breakdown selector
    with col1:
        selected_breakdown = st.selectbox("🔎 Breakdown by", breakdown_options)

    # Metric selector
    with col2:
        selected_metric_label = st.selectbox("📌 Metric", list(metric_options.keys()))
        selected_metric = metric_options[selected_metric_label]

    # Plot type selector
    with col3:
        plot_types = ["Bar", "Pie", "Line"]
        selected_plot = st.selectbox("📊 Plot type", plot_types)


    #Generate title
    title = f"Accidents by {selected_breakdown} using a {selected_plot} plot"
    # -------------------
    #   AGGREGATION
    # -------------------

    if selected_metric is None:
        # Count number of accidents
        grouped = (
            df.groupby(selected_breakdown)
              .size()
              .reset_index(name="value")
        )
    else:
        # Sum injuries/fatalities
        grouped = (
            df.groupby(selected_breakdown)[selected_metric]
              .sum()
              .reset_index(name="value")
        )

    grouped = grouped.sort_values(selected_breakdown)



    # -------------------
    #   PLOTTING
    # -------------------

    if selected_plot == "Bar":
        fig = px.bar(
            grouped,
            x=selected_breakdown,
            y="value",
            text="value",
            labels={selected_breakdown: selected_breakdown.capitalize(),
                    "value": selected_metric_label},
            title=title
        )
        fig.update_traces(textposition="outside")

    elif selected_plot == "Pie":
        fig = px.pie(
            grouped,
            names=selected_breakdown,
            values="value",
            title=title
        )

    elif selected_plot == "Line":
        fig = px.line(
            grouped,
            x=selected_breakdown,
            y="value",
            markers=True,
            labels={selected_breakdown: selected_breakdown.capitalize(),
                    "value": selected_metric_label},
            title=title
        )

    st.plotly_chart(fig, use_container_width=True)