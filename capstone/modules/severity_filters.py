import pandas as pd
import streamlit as st

def apply_severity_filters(df):
    df_filtered = df.copy()

    #1 Severity filters
    severity_toggle = st.sidebar.toggle("**Accident severity filters**", True)


    if not severity_toggle:
        return df_filtered

    # 2 Light accidents
    if st.sidebar.toggle("Filter by number of minor injuries", True):

        only_zero_light = st.sidebar.checkbox("Only accidents with 0 minor injuries")

        if only_zero_light:
            df_filtered = df_filtered[df_filtered["minor_injuries_30d"] == 0]

        else:
            light_range = st.sidebar.slider(
                "Victims with minor injuries",
                min_value=int(df["minor_injuries_30d"].min()),
                max_value=int(df["minor_injuries_30d"].max()),
                value=(int(df["minor_injuries_30d"].min()), int(df["minor_injuries_30d"].max()))
            )
            df_filtered = df_filtered[df_filtered["minor_injuries_30d"].between(*light_range)]

    #2 Severe accidents
    if st.sidebar.toggle("Filter by number of severe injuries", False):
        light_range = st.sidebar.slider(
            "Victims with severe injuries",
            min_value=int(df["serious_injuries_30d"].min()),
            max_value=int(df["serious_injuries_30d"].max()),
            value=(int(df["serious_injuries_30d"].min()), int(df["serious_injuries_30d"].max()))
        )
        df_filtered = df_filtered[df_filtered["serious_injuries_30d"].between(*light_range)]

    #2 Fatal accidents
    df_filtered = add_injury_filter(df,column="fatalities_30d",label="fatalities")


    return df_filtered


def add_injury_filter(
    df: pd.DataFrame,
    column: str,
    label: str
) -> pd.DataFrame:
    """
    Adds a sidebar filter for injury counts using a toggle, slider,
    and a checkbox that forces only zero injuries.

    Parameters
    ----------
    df : DataFrame
        Original dataframe for min/max calculation.
    column : str
        Column name with injury counts.
    label : str
        Label shown in the slider.

    Returns
    -------
    df_filtered : DataFrame
        The filtered dataframe.
    """

    if st.sidebar.toggle(f"Filter by number of {label}", False):

        # Checkbox option: only 0 injuries
        only_zero = st.sidebar.checkbox(f"Only accidents with 0 {label.lower()}")

        if only_zero:
            return df[df[column] == 0]

        # Otherwise: slider
        min_val = int(df[column].min())
        max_val = int(df[column].max())

        value_range = st.sidebar.slider(
            f"Victims with {label}",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val)
        )

        return df[df[column].between(*value_range)]

    return df
