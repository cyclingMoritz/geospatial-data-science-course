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

def create_map(gdf, boundary_gdf):

    if len(gdf) > 0:
        center = [gdf["latitude"].mean(), gdf["longitude"].mean()]
    else:
        center = [boundary_gdf["lat"].mean(), boundary_gdf["lon"].mean()]

    m = folium.Map(location=center, zoom_start=12, tiles="CartoDB Positron")

    # Add Lisbon boundary polygons
    for _, r in boundary_gdf.iterrows():
        sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
        folium.GeoJson(sim_geo.to_json(), style_function=lambda x: {"fillColor": "orange"}).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)
    for _, row in gdf.iterrows():

        # popup_html = f"""
        # <div style="font-size:14px; line-height:1.4;">
        #     <b style="font-size:16px;">Accident ID: {row['id']}</b><br><br>

        #     <b>Date:</b> {date_str}<br>
        #     <b>Weekday:</b> {row['weekday']}<br>
        #     <b>Hour:</b> {row['hour']}<br>
        #     <b>Minor Injuries:</b> {row['minor_injuries_30d']}<br>
        #     <b>Serious Injuries:</b> {row['serious_injuries_30d']}<br>
        #     <b>Fatalities:</b> {row['fatalities_30d']}<br>
        # </div>
        # """
        popup_html = f"""
            <table style="width:220px; font-size:14px; border-collapse:collapse; line-height:1.4;">
                <tr>
                    <th colspan="2" style="font-size:16px; text-align:center; padding:6px 0;">
                        Accident {row['id']}
                    </th>
                </tr>

                <tr><td><b>Date</b></td><td>{row["date_str"]}</td></tr>
                <tr><td><b>Weekday</b></td><td>{row['weekday']}</td></tr>
                <tr><td><b>Hour</b></td><td>{row['hour']}</td></tr>

                <tr><td><b>Minor Injuries</b></td><td>{row['minor_injuries_30d']}</td></tr>
                <tr><td><b>Serious Injuries</b></td><td>{row['serious_injuries_30d']}</td></tr>
                <tr><td><b>Fatalities</b></td><td>{row['fatalities_30d']}</td></tr>
            </table>
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

    return m
