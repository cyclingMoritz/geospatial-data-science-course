import pandas as pd
import streamlit as st

def apply_temporal_filters(df,default=False):
    df_filtered = df.copy()
    
    #1 Temporal filters
    temporal_toggle = st.sidebar.toggle("**Temporal filters**", default)
    #Generate the date attribute
    date_str = df["day"].astype(str).str.zfill(2) + " " + df["month"].astype(str) + " 2023"
    df_filtered["date"] = pd.to_datetime(date_str, errors="coerce")
    df_filtered["date_str"] = df_filtered["date"].dt.strftime("%d %b %Y")


    if not temporal_toggle:
        return df_filtered

    #2 Filter by values
    if st.sidebar.toggle("Filter by value", False):
        weekday_options = df["weekday"].dropna().unique()
        selected_weekdays = st.sidebar.multiselect(
            "Filter by Weekday", weekday_options, default=weekday_options
        )
        df_filtered = df_filtered[df_filtered["weekday"].isin(selected_weekdays)]

        month_options = df["month"].dropna().unique()
        selected_months = st.sidebar.multiselect(
            "Filter by Month", month_options, default=month_options
        )
        df_filtered = df_filtered[df_filtered["month"].isin(selected_months)]

    #2 Filter by ranges
    if st.sidebar.toggle("Filter by range", False):

        hour_range = st.sidebar.slider(
            "Filter by Hour",
            min_value=int(df["hour"].min()),
            max_value=int(df["hour"].max()),
            value=(int(df["hour"].min()), int(df["hour"].max()))
        )
        df_filtered = df_filtered[df_filtered["hour"].between(*hour_range)]

        day_range = st.sidebar.slider(
            "Filter by Day",
            min_value=int(df["day"].min()),
            max_value=int(df["day"].max()),
            value=(int(df["day"].min()), int(df["day"].max()))
        )
        df_filtered = df_filtered[df_filtered["day"].between(*day_range)]

    #2 Filter by date interval
    if st.sidebar.toggle("Filter between dates", False):
        date_interval = st.sidebar.date_input(
            "Pick to dates to use for filtering",
            (df_filtered["date"].min(), df_filtered["date"].max())
        )

        start, end = pd.to_datetime(date_interval[0]), pd.to_datetime(date_interval[1])
        df_filtered = df_filtered[(df_filtered["date"] >= start) & (df_filtered["date"] <= end)]

    #1 Filter by severity
    


    return df_filtered
