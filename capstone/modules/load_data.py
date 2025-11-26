import pandas as pd
import osmnx as ox

def load_accident_data(path="data/Road_Accidents_Lisbon.csv"):
    df = pd.read_csv(path)
    return df

def load_boundary(city="Lisbon, Portugal", epsg=4326):
    gdf = ox.geocode_to_gdf(city)
    gdf = gdf.to_crs(epsg=epsg)

    union = gdf.unary_union
    if union.geom_type == "MultiPolygon":
        boundary = max(union, key=lambda p: p.area)
    else:
        boundary = union

    return gdf, boundary
