import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
from streamlit_folium import st_folium
import osmnx as ox

# Page configuration
st.set_page_config(page_title="Lisbon Road Accidents", layout="wide")

# Title and description
st.title("Lisbon Road Accidents – Interactive Dashboard")


# Load dataset
df = pd.read_csv("data/Road_Accidents_Lisbon.csv")
st.header("Accident Data Overview")


# Get Lisbon administrative boundary as a single Polygon (in EPSG:4326)
boundary_gdf = ox.geocode_to_gdf("Lisbon, Portugal")
boundary_gdf = boundary_gdf.to_crs(epsg=4326)
boundary_union = boundary_gdf.unary_union
# if result is a MultiPolygon, keep the largest component
if boundary_union.geom_type == "MultiPolygon":
    boundary_lisbon = max(boundary_union, key=lambda p: p.area)
else:
    boundary_lisbon = boundary_union


accident_overview = {
    "Number accidents": len(df),
    "Number fatalities": df["fatalities_30d"].sum(),
    "Number serious injuries": df["serious_injuries_30d"].sum(),
    "Number minor injuries": df["minor_injuries_30d"].sum(),
}
st.markdown(f"""During the year 2023, a total of **{accident_overview["Number accidents"]}** 
                accidents were recorded in the city of Lisbon.
                These accidents resulted in **{accident_overview["Number fatalities"]}**
                fatalities, **{accident_overview["Number serious injuries"]}**
                serious injuries and **{accident_overview["Number minor injuries"]}**
                minor injuries.
            """)

attributes = str(df.columns.to_list()).replace("'","").replace("[","").replace("]","")
st.markdown(f""" Of these accidents, we know various details such as {attributes}.
            """)

dataset_inspection = {
    "Columns": df.shape[1],
    "Rows": df.shape[0],
    "Missing values": df.isnull().sum().sum(),
    "Duplicate rows": df.duplicated().sum(),
}

st.markdown("Some other key characteristics of the dataset are that the number of missing values is "
            f"**{dataset_inspection['Missing values']}** and the number of duplicate rows is "
            f"**{dataset_inspection['Duplicate rows']}**. Below, the first few rows of the dataset are shown:"
            )

st.dataframe(df.head())


# Sidebar filter by weekday
st.sidebar.header("Filter Options")

temporal_toggle = st.sidebar.toggle("**Temporal filters**", value=True)


if temporal_toggle:

    toggle_by_values = st.sidebar.toggle("Filter by value", value=True)
    if toggle_by_values:
         
        #Filter by weekday
        weekday_options = df["weekday"].dropna().unique()
        selected_weekdays = st.sidebar.multiselect("Filter by Weekday", weekday_options, default=weekday_options)
       
        #Filter by month
        month_options = df["month"].dropna().unique()
        selected_months = st.sidebar.multiselect("Filter by Month", month_options, default=month_options)

    #    #Filter by hour
    #     hour_options = df["hour"].dropna().unique()
    #     selected_days = st.sidebar.multiselect("Filter by Hour", hour_options, default=hour_options)

    #     #Filter by day 
    #     day_options = df["day"].dropna().unique()
    #     selected_days = st.sidebar.multiselect("Filter by Day", day_options, default=day_options)
    
    
    toggle_by_range = st.sidebar.toggle("Filter by range", value=False)
    if toggle_by_range:

            #Filter by hour
        hour_options = df["hour"].dropna().unique()
        hour = [df["hour"].min(),df["hour"].max()]
        selected_hours_range = st.sidebar.slider("Filter by Hour",  
                                                min_value=hour[0], 
                                                max_value=hour[1], 
                                                value=(hour[0],hour[1])
                                                )

        #Filter by day 
        day_options = df["day"].dropna().unique()
        day = [df["day"].min(),df["day"].max()]
        selected_days_range = st.sidebar.slider("Filter by Day",  
                                                min_value=day[0], 
                                                max_value=day[1], 
                                                value=(day[0],day[1])
                                                )
    
    toggle_between_dates = st.sidebar.toggle("Filter between dates", value=False)
    if toggle_between_dates:

        # create a proper datetime column from day (int) and month (English name) for year 2023
        date_str = df["day"].astype(str).str.zfill(2) + " " + df["month"].astype(str) + " 2023"
        df["date"] = pd.to_datetime(date_str, format="%d %B %Y", errors="coerce")
        # fallback parse for any remaining unparsable values (e.g., abbreviated month names)
        if df["date"].isna().any():
            df.loc[df["date"].isna(), "date"] = pd.to_datetime(date_str[df["date"].isna()], errors="coerce")
        dates = [df["date"].min(),df["date"].max()]
        date_interval = st.sidebar.date_input(
            "Pick to dates to use for filtering",
            (dates[0], dates[1]),
            dates[0],
            dates[1],
            format="DD/MM/YYYY",
        )

# apply only the filters that were created/used by the sidebar widgets
df_filtered = df.copy()

# Weekday filter
try:
    if selected_weekdays is not None and len(selected_weekdays) > 0:
        df_filtered = df_filtered[df_filtered["weekday"].isin(selected_weekdays)]
except NameError:
    pass

# Month filter
try:
    if selected_months is not None and len(selected_months) > 0:
        df_filtered = df_filtered[df_filtered["month"].isin(selected_months)]
except NameError:
    pass

# Numeric range filter (slider). The original code used the same variable for hour/day sliders,
# so apply it to whichever columns exist in the dataframe.
try:
    if selected_days_range is not None and isinstance(selected_days_range, (list, tuple)) and len(selected_days_range) == 2:
        lo, hi = selected_hours_range
        if "hour" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["hour"].between(lo, hi)]
        lo, hi = selected_days_range
        if "day" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["day"].between(lo, hi)]
except NameError:
    pass

# Date interval filter
try:
    if date_interval is not None and "date" in df_filtered.columns:
        start, end = date_interval
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)
        df_filtered = df_filtered[(df_filtered["date"] >= start) & (df_filtered["date"] <= end)]
except NameError:
    pass

#Check we have valid rows
if len(df_filtered)>=1:
    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df_filtered,
        geometry=[Point(xy) for xy in zip(df_filtered["longitude"], df_filtered["latitude"])],
        crs="EPSG:4326"
    )

    # Center map on Lisbon
    center = [gdf["latitude"].mean(), gdf["longitude"].mean()]
else:

    center = [boundary_gdf["lat"], boundary_gdf["lon"]]
m = folium.Map(location=center, zoom_start=12, tiles="CartoDB Positron")

try:
    for _, row in gdf.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=5,
            color="red",
            fill=True,
            fill_opacity=0.6,
            popup=f"ID: {row['id']}<br>Weekday: {row['weekday']}<br>Fatalities: {row['fatalities_30d']}"
        ).add_to(m)
except:
    pass

for _, r in boundary_gdf.iterrows():
    # Without simplifying the representation of each borough,
    # the map might not be displayed
    sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {"fillColor": "orange"})
    geo_j.add_to(m)

# Show map
st.subheader("Accident Map")
st_data = st_folium(m, width=800, height=600)


