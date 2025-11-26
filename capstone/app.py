import streamlit as st
from streamlit_folium import st_folium

from modules.load_data import load_accident_data
from modules.boundary import load_boundary
from modules.stats import compute_overview, dataset_inspection
from modules.temporal_filters import apply_temporal_filters
from modules.severity_filters import apply_severity_filters
from modules.map_utils import df_to_gdf, create_map
from modules.plots import plot_accident_data

st.set_page_config(page_title="Lisbon Road Accidents", layout="wide")
st.title("Lisbon Road Accidents – Interactive Dashboard")

# Load data
df = load_accident_data()
boundary_gdf, boundary_lisbon = load_boundary()

# Show stats
st.header("Accident Data Overview")
overview = compute_overview(df)
st.markdown(f"""During the year 2023, a total of **{overview["Number accidents"]}** 
                accidents were recorded in the city of Lisbon.
                These accidents resulted in **{overview["Number fatalities"]}**
                fatalities, **{overview["Number serious injuries"]}**
                serious injuries and **{overview["Number minor injuries"]}**
                minor injuries.
            """)

attributes = str(df.columns.to_list()).replace("'","").replace("[","").replace("]","")
st.markdown(f""" Of these accidents, we know various details such as {attributes}.
            """)

inspec = dataset_inspection(df)

st.markdown("Some other key characteristics of the dataset are that the number of missing values is "
            f"**{inspec['Missing values']}** and the number of duplicate rows is "
            f"**{inspec['Duplicate rows']}**. Below, the first few rows of the dataset are shown below:"
            )
st.dataframe(df.head())


# Apply sidebar filters
st.sidebar.header("Filter Options")
df_filtered = apply_temporal_filters(df)
df_filtered = apply_severity_filters(df_filtered)

#Generate plots
plot_accident_data(df_filtered)



# Create map
gdf = df_to_gdf(df_filtered)
m = create_map(gdf, boundary_gdf)

# Display map
st.subheader("Accident Map")
st_folium(m, width=800, height=600)
