import pandas as pd

def load_accident_data(path="data/Road_Accidents_Lisbon.csv"):
    df = pd.read_csv(path)
    return df
