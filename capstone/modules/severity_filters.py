import pandas as pd
import streamlit as st

def apply_severity_filters(df, container=st.sidebar, expanded=False):
    """
    Apply severity filters (minor, serious, fatal) to a dataframe.
    Can render in sidebar, container, or column.
    """


    df_filtered = df.copy()
    with st.expander("**Accident severity filters**",expanded=expanded):
        # ---- Minor injuries ----
        df_filtered = add_injury_filter(df_filtered, column="minor_injuries_30d",
                                        label="minor injuries", container=container)
        # ---- Serious injuries ----
        df_filtered = add_injury_filter(df_filtered, column="serious_injuries_30d",
                                        label="serious injuries", container=container)
        # ---- Fatalities ----
        df_filtered = add_injury_filter(df_filtered, column="fatalities_30d",
                                        label="fatalities", container=container)

    return df_filtered


def add_injury_filter(df: pd.DataFrame, column: str, label: str, container=None) -> pd.DataFrame:
    """
    Adds a filter for injury counts using toggle, slider, and optional checkbox.
    Works in any Streamlit container.
    """
    if container is None:
        container = st.sidebar  # fallback

    if container.toggle(f"Filter by number of {label}", False):
        # Checkbox option: only 0 injuries
        only_zero = container.checkbox(f"Only accidents with 0 {label.lower()}")
        if only_zero:
            return df[df[column] == 0]

        # Otherwise: slider
        min_val = int(df[column].min())
        max_val = int(df[column].max())
        value_range = container.slider(
            f"Victims with {label}",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val)
        )
        return df[df[column].between(*value_range)]

    return df


#Initial version
    # if st.sidebar.toggle("Filter by number of minor injuries", True):

    #     only_zero_light = st.sidebar.checkbox("Only accidents with 0 minor injuries")

    #     if only_zero_light:
    #         df_filtered = df_filtered[df_filtered["minor_injuries_30d"] == 0]

    #     else:
    #         light_range = st.sidebar.slider(
    #             "Victims with minor injuries",
    #             min_value=int(df["minor_injuries_30d"].min()),
    #             max_value=int(df["minor_injuries_30d"].max()),
    #             value=(int(df["minor_injuries_30d"].min()), int(df["minor_injuries_30d"].max()))
    #         )
    #         df_filtered = df_filtered[df_filtered["minor_injuries_30d"].between(*light_range)]
