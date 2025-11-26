import pandas as pd
import streamlit as st

def apply_temporal_filters(df, container=None, expanded=True):
    """
    Apply temporal filters to a dataframe. Can render in sidebar or in any Streamlit container.
    
    Args:
        df: DataFrame to filter
        container: Streamlit container (st.sidebar, st.container, or a column)
        default: default toggle value for enabling temporal filters
    
    Returns:
        Filtered DataFrame
    """
    df_filtered = df.copy()
    with st.expander("**Temporal filters**",expanded=expanded):

        # ---- Filter by values ----
        if container.toggle("Filter by value", False):
            weekday_options = df["weekday"].dropna().unique()
            selected_weekdays = container.multiselect(
                "Filter by Weekday", weekday_options, default=weekday_options
            )
            df_filtered = df_filtered[df_filtered["weekday"].isin(selected_weekdays)]

            month_options = df["month"].dropna().unique()
            selected_months = container.multiselect(
                "Filter by Month", month_options, default=month_options
            )
            df_filtered = df_filtered[df_filtered["month"].isin(selected_months)]

        # ---- Filter by ranges ----
        if container.toggle("Filter by range", False):
            hour_range = container.slider(
                "Filter by Hour",
                min_value=int(df["hour"].min()),
                max_value=int(df["hour"].max()),
                value=(int(df["hour"].min()), int(df["hour"].max()))
            )
            df_filtered = df_filtered[df_filtered["hour"].between(*hour_range)]

            day_range = container.slider(
                "Filter by Day",
                min_value=int(df["day"].min()),
                max_value=int(df["day"].max()),
                value=(int(df["day"].min()), int(df["day"].max()))
            )
            df_filtered = df_filtered[df_filtered["day"].between(*day_range)]

        # ---- Filter by date interval ----
        if container.toggle("Filter between dates", False):
            date_interval = container.date_input(
                "Pick two dates for filtering",
                (df_filtered["date"].min(), df_filtered["date"].max())
            )
            start, end = pd.to_datetime(date_interval[0]), pd.to_datetime(date_interval[1])
            df_filtered = df_filtered[(df_filtered["date"] >= start) & (df_filtered["date"] <= end)]

    return df_filtered
