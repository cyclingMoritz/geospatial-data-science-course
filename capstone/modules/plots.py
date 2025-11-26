import streamlit as st
import pandas as pd
import plotly.express as px

def plot_accident_data(df):

    # ---- Fix ordering for month and weekday ----
    MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]

    WEEKDAY_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]


    if "month" in df.columns:
        df["month"] = pd.Categorical(df["month"], categories=MONTH_ORDER, ordered=True)

    if "weekday" in df.columns:
        df["weekday"] = pd.Categorical(df["weekday"], categories=WEEKDAY_ORDER, ordered=True)

    # ---- Breakdown options ----
    breakdown_options = ["month", "day", "hour", "weekday", "municipality"]

    # ---- Metric options ----
    metric_options = {
        "Number of accidents": None,
        "Minor injuries": "minor_injuries_30d",
        "Serious injuries": "serious_injuries_30d",
        "Fatalities": "fatalities_30d"
    }

    col1, col2, col3 = st.columns(3)

    # Breakdown selector
    with col1:
        selected_breakdown = st.selectbox("🔎 Breakdown by", breakdown_options)

    # Multi-metric selector
    with col2:
        selected_metric_labels = st.multiselect(
            "📌 Select metric(s)",
            list(metric_options.keys()),
            default=["Number of accidents"]
        )
        selected_metrics = [metric_options[label] for label in selected_metric_labels]

    # Plot type selector
    with col3:
        plot_types = ["Bar", "Line", "Pie"]
        selected_plot = st.selectbox("📊 Plot type", plot_types)

    # ---------------------
    # PIE CHART VALIDATION
    # ---------------------
    if selected_plot == "Pie" and len(selected_metrics) != 1:
        st.warning("⚠️ Pie charts require selecting exactly **1 metric**. Please adjust the metric selection.")
        return  # Stop here safely, no exception raised


    # ---------------------
    # GENERATE DYNAMIC TITLE
    # ---------------------

    # Human-friendly names for metrics
    pretty_metric_labels = ", ".join(selected_metric_labels)

    # Nice formatting for the breakdown
    pretty_breakdown = selected_breakdown.replace("_", " ").capitalize()

    # Pie rule: only one metric allowed
    if selected_plot == "Pie":
        title = f"{selected_metric_labels[0]} by {pretty_breakdown}"
    else:
        # Multiple metrics → pluralize
        if len(selected_metric_labels) > 1:
            title = f"Metrics ({pretty_metric_labels}) by {pretty_breakdown}"
        else:
            title = f"{selected_metric_labels[0]} by {pretty_breakdown}"

    # Add plot type
    title += f" — {selected_plot} plot"

    # ---------------------
    # AGGREGATION
    # ---------------------

    aggregated = pd.DataFrame()

    for label, metric in zip(selected_metric_labels, selected_metrics):

        if metric is None:
            # Count accidents
            grouped = (
                df.groupby(selected_breakdown)
                  .size()
                  .reset_index(name="value")
            )
        else:
            # Sum injuries/fatalities
            grouped = (
                df.groupby(selected_breakdown)[metric]
                  .sum()
                  .reset_index(name="value")
            )

        grouped["metric"] = label
        aggregated = pd.concat([aggregated, grouped], ignore_index=True)

    # Sort by breakdown for readability
    aggregated = aggregated.sort_values(selected_breakdown)


    # ---------------------
    # PLOTTING
    # ---------------------

    try:
        if selected_plot == "Bar":
            fig = px.bar(
                aggregated,
                x=selected_breakdown,
                y="value",
                color="metric",
                barmode="group",
                text="value",
                labels={selected_breakdown: selected_breakdown.capitalize(), "value": "Value"},
                title=title
            )
            fig.update_traces(textposition="outside")

        elif selected_plot == "Line":
            fig = px.line(
                aggregated,
                x=selected_breakdown,
                y="value",
                color="metric",
                markers=True,
                labels={selected_breakdown: selected_breakdown.capitalize(), "value": "Value"},
                title=title
            )

        elif selected_plot == "Pie":
            # Only one metric here (validated above)
            metric_label = selected_metric_labels[0]
            filtered = aggregated[aggregated["metric"] == metric_label]

            fig = px.pie(
                filtered,
                names=selected_breakdown,
                values="value",
                title=f"{title} — {metric_label}"
            )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ An error occurred during plotting: {e}")
