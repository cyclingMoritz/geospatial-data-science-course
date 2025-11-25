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
