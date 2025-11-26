import streamlit as st
from streamlit_folium import st_folium

from modules.load_data import load_accident_data, load_boundary
from modules.stats import load_data,compute_overview, dataset_inspection
from modules.temporal_filters import apply_temporal_filters
from modules.severity_filters import apply_severity_filters
from modules.map_utils import df_to_gdf, create_map
from modules.plots import plot_accident_data, accident_plot

st.set_page_config(page_title="Lisbon Road Accidents", layout="wide")
st.title("Lisbon Road Accidents – Interactive Dashboard")

# Load data
try:
    df = load_accident_data()
    clean_df = load_data(df)
    boundary_gdf, boundary_lisbon = load_boundary()

except Exception as e:
    st.error(f"❌ An error occurred loading the data: {e}")


# Show stats
st.header("Accident Data Overview")
overview = compute_overview(df)
attributes = str(df.columns.to_list()).replace("'", "").replace("[", "").replace("]", "")
inspec = dataset_inspection(df)

st.markdown(
    "During the year 2023, a total of **{num_acc}** accidents were recorded in the city of Lisbon. "
    "These accidents resulted in **{num_fatal}** fatalities, **{num_serious}** serious injuries, "
    "and **{num_minor}** minor injuries. Of these accidents, we know various details such as {attrs}. "
    "Some other key characteristics of the dataset are that the number of missing values is "
    "**{missing}** and the number of duplicate rows is **{duplicates}**. Below, the first few rows of the dataset are shown:"
    .format(
        num_acc=overview["Number accidents"],
        num_fatal=overview["Number fatalities"],
        num_serious=overview["Number serious injuries"],
        num_minor=overview["Number minor injuries"],
        attrs=attributes,
        missing=inspec["Missing values"],
        duplicates=inspec["Duplicate rows"]
    )
)

st.dataframe(df.head())

# Show stats
st.header("Main takeaways from exploring the data temporally")

# Monthly distribution
st.markdown(
    "Analyzing the distribution of accidents by month, we observe that totals range from **140 accidents in February** "
    "to **208 in May**. Other notable peaks occur in March (**206 accidents**) and October (**202 accidents**), while "
    "the lower months include December (**155 accidents**) and August (**158 accidents**). "
    "The lower accident counts in August and December may be explained by the increased number of holidays, resulting "
    "in fewer people commuting. February is also low, likely due to having fewer days; however, when adjusting for the "
    "number of days (accidents per day), February performs similarly to December and August, suggesting that additional "
    "factors may influence these variations."
)
with st.expander("Show monthly accidents plot"):
    accident_plot(clean_df, "month", ["Number of accidents"], [None], "Bar")

# Minor, serious, and fatal injuries
st.markdown(
    "A similar trend is observed for minor injuries, which represent the majority of accidents and therefore follow a similar pattern. "
    "Incidents with serious injuries display a different pattern: January shows a spike with **10 serious injuries**, while June only has **1 serious injury**."
    "The January peak could initially suggest drunk driving or New Year's morning accidents, "
    "but this hypothesis is not supported when looking at the daily distribution. Fatal accidents show yet another pattern, likely due to the low overall numbers: "
    "July has a spike of **2 fatalities**, while no fatal accidents occur in April, October, November, and December, and the remaining months report only **1 fatality** each."
)
with st.expander("Show accidents by injury level per month"):
    accident_plot(clean_df, "month", ["Minor injuries","Serious injuries","Fatalities"], ["minor_injuries_30d","serious_injuries_30d","fatalities_30d"], "Line")

# Weekday distribution
st.markdown(
    "Examining the distribution by weekday, accidents tend to be more frequent on Thursdays and Fridays, with lower numbers on Saturdays and Sundays. "
    "This trend is consistent for minor injuries, while serious injuries show a peak on Mondays with **10 accidents**. Fatal accidents are more erratic, "
    "with the maximum values occurring on Sundays and Tuesdays, and none recorded on Mondays, Fridays, or Saturdays."
)
with st.expander("Show accidents per weekday"):
    accident_plot(clean_df, "weekday", ["Number of accidents"], [None], "Pie")

# Hourly distribution
st.markdown(
    "Hourly distribution shows peaks during the evening between 16:00–19:00, as well as around 13:00 and 09:00, "
    "the latter two potentially related to children entering or leaving school. Nighttime hours show a decreasing trend from 20:00 to 05:00, "
    "after which the number of accidents starts to increase again."
)
with st.expander("Show a plot of accidents per hour"):
    accident_plot(clean_df, "hour", ["Number of accidents"], [None], "Bar")

# Day-of-month distribution
st.markdown(
    "Looking at the distribution by day of the month, the 21st shows the highest number of accidents, followed by the 13th and 6th, "
    "while the 31st shows the lowest count, likely because not all months have this day. "
    "The single day with the most accidents is March 21st, with **14 accidents** and **15 minor injuries**, whereas the day with the most injured individuals is June 22nd, "
    "with **18 victims**."
)

# Apply sidebar filters
st.sidebar.header("Filter Options")
df_filtered = apply_temporal_filters(clean_df,False)
df_filtered = apply_severity_filters(df_filtered,False)

with st.expander("📊 Wanna explore more? Set your own filters!", expanded=True):
    # Generate the interactive plots with the filtered data
    plot_accident_data(df_filtered)




# Create map
gdf = df_to_gdf(df_filtered)
map_html = create_map(gdf, boundary_gdf)
# Display map
st.subheader("Accident Map")
st.components.v1.html(map_html, height=500, scrolling=False)

# st_folium(m, width=800, height=600, returned_objects=None)
