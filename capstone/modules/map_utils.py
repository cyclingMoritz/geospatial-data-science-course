import geopandas as gpd
from shapely.geometry import Point
import folium

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

    # Add accident points
    for _, row in gdf.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=5,
            color="red",
            fill=True,
            fill_opacity=0.6,
            popup=f"ID: {row['id']}<br>Weekday: {row['weekday']}<br>Fatalities: {row['fatalities_30d']}",
        ).add_to(m)

    # Add Lisbon boundary polygons
    for _, r in boundary_gdf.iterrows():
        sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
        folium.GeoJson(sim_geo.to_json(), style_function=lambda x: {"fillColor": "orange"}).add_to(m)

    return m
