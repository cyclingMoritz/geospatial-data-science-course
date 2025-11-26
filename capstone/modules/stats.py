import pandas as pd

def load_data(df):
    clean_data = df.copy()
    
    #Generate the date attribute
    date_str = clean_data["day"].astype(str).str.zfill(2) + " " + clean_data["month"].astype(str) + " 2023"
    clean_data["date"] = pd.to_datetime(date_str, errors="coerce")
    clean_data["date_str"] = clean_data["date"].dt.strftime("%d %b %Y")

    # Make temporal attributes ordered
    return clean_data


def compute_overview(df):
    return {
        "Number accidents": len(df),
        "Number fatalities": df["fatalities_30d"].sum(),
        "Number serious injuries": df["serious_injuries_30d"].sum(),
        "Number minor injuries": df["minor_injuries_30d"].sum(),
    }

def dataset_inspection(df):
    return {
        "Columns": df.shape[1],
        "Rows": df.shape[0],
        "Missing values": df.isnull().sum().sum(),
        "Duplicate rows": df.duplicated().sum(),
    }
