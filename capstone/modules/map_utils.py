import streamlit as st   # <--- add this at the top
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import MarkerCluster
import pandas as pd

def df_to_gdf(df):
    return gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df["longitude"], df["latitude"])],
        crs="EPSG:4326"
    )


# @st.cache_data
def create_map(_gdf, _boundary_gdf):

    if len(_gdf) > 0:
        center = [_gdf["latitude"].mean(), _gdf["longitude"].mean()]
    else:
        center = [_boundary_gdf["lat"].mean(), _boundary_gdf["lon"].mean()]

    m = folium.Map(location=center, zoom_start=12, tiles="CartoDB Positron")

    # Add Lisbon boundary polygons
    boundary_fg = folium.FeatureGroup(name="Lisbon Boundary")
    for _, r in _boundary_gdf.iterrows():
        sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
        folium.GeoJson(sim_geo.to_json(), style_function=lambda x: {"fillColor": "orange"}).add_to(boundary_fg)
    boundary_fg.add_to(m)   

    if len(_gdf) > 0:
        points_fg = folium.FeatureGroup(name="Accidents")
        marker_cluster = MarkerCluster().add_to(points_fg)
        for _, row in _gdf.iterrows():
            date_str = pd.to_datetime(row["date"]).strftime("%d %b %Y")
            popup_html = f"""
            <div style="font-size:14px; line-height:1.4;">
                <b style="font-size:16px;">Accident ID: {row['id']}</b><br><br>
                <b>Date:</b> {date_str}<br>
                <b>Weekday:</b> {row['weekday']}<br>
                <b>Hour:</b> {row['hour']}<br>
                <b>Minor Injuries:</b> {row['minor_injuries_30d']}<br>
                <b>Serious Injuries:</b> {row['serious_injuries_30d']}<br>
                <b>Fatalities:</b> {row['fatalities_30d']}<br>
            </div>
            """
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=7,
                color="#8B0000",
                weight=2,
                fill=True,
                fill_opacity=0.8,
                fill_color="#FF3333",
                popup=folium.Popup(popup_html, max_width=300),
            ).add_to(marker_cluster)
    points_fg.add_to(m)
    # ----------------------
    # Add LayerControl
    # ----------------------
    folium.LayerControl(collapsed=False).add_to(m)
    # Instead of caching the map, cache the HTML string
    return m._repr_html_()
