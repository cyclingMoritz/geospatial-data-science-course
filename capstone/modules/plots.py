import streamlit as st
import pandas as pd
import plotly.express as px

def accident_plot_controls(df):
    """Display selectors and return the user choices."""

    # ---- Fix ordering for month and weekday ----
    MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]

    WEEKDAY_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

    if "month" in df.columns:
        df["month"] = pd.Categorical(df["month"], categories=MONTH_ORDER, ordered=True)

    if "weekday" in df.columns:
        df["weekday"] = pd.Categorical(df["weekday"], categories=WEEKDAY_ORDER, ordered=True)

    # ---- Breakdown options ----
    breakdown_options = ["month","weekday", "hour", "day","date"]

    # ---- Metric options ----
    df["total_victims"] = df["minor_injuries_30d"] + df["serious_injuries_30d"] + df["fatalities_30d"]
    metric_options = {
        "Number of accidents": None,
        "Minor injuries": "minor_injuries_30d",
        "Serious injuries": "serious_injuries_30d",
        "Fatalities": "fatalities_30d",
        "Total number of victims":"total_victims"
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


    #Make plot
    accident_plot(df, selected_breakdown, selected_metric_labels, selected_metrics, selected_plot,"Dinamic_version")
    return df, selected_breakdown, selected_metric_labels, selected_metrics, selected_plot

# ---------------------     

# 2️⃣ Plotting function
# ---------------------
def accident_plot(df, breakdown, metric_labels, metrics, plot_type, key=None):
    """Generate the plot based on the selected parameters."""

    # ---------------------
    # Validation
    # ---------------------
    if plot_type == "Pie" and len(metrics) != 1:
        st.warning("⚠️ Pie charts require exactly **1 metric**.")
        return

    if len(metrics) == 0:
        st.warning("⚠️ Please select at least one metric.")
        return

    # ---------------------
    # Aggregation
    # ---------------------
    aggregated = pd.DataFrame()

    for label, metric in zip(metric_labels, metrics):
        if metric is None:
            grouped = df.groupby(breakdown, observed=True).size().reset_index(name="value")
            metric = "Number of accidents"
        else:
            grouped = df.groupby(breakdown)[metric].sum().reset_index(name="value")

        grouped["metric"] = label
        aggregated = pd.concat([aggregated, grouped], ignore_index=True)

    aggregated = aggregated.sort_values(breakdown)

    # ---------------------
    # Dynamic title
    # ---------------------
    pretty_metric_labels = ", ".join(metric_labels)
    pretty_breakdown = breakdown.replace("_", " ").capitalize()

    if plot_type == "Pie":
        title = f"{metric_labels[0]} by {pretty_breakdown}"
    else:
        title = f"{'Metrics (' + pretty_metric_labels + ')' if len(metric_labels) > 1 else metric_labels[0]} by {pretty_breakdown}"

    title += f" — {plot_type} plot"

    # ---------------------
    # Plotting
    # ---------------------
    try:
        if plot_type == "Bar":
            fig = px.bar(
                aggregated,
                x=breakdown,
                y="value",
                color="metric",
                barmode="group",
                text="value",
                labels={breakdown: pretty_breakdown, "value": "Value"},
                title=title
            )
            fig.update_traces(textposition="outside")

        elif plot_type == "Line":
            fig = px.line(
                aggregated,
                x=breakdown,
                y="value",
                color="metric",
                markers=True,
                labels={breakdown: pretty_breakdown, "value": "Value"},
                title=title
            )

        elif plot_type == "Pie":
            filtered = aggregated[aggregated["metric"] == metric_labels[0]]
            fig = px.pie(
                filtered,
                names=breakdown,
                values="value",
                title=title
            )
        
        st.plotly_chart(fig, width='stretch',key=key)

    except Exception as e:
        st.error(f"❌ An error occurred during plotting: {e}")