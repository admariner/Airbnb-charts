import numpy as np
import pandas as pd
path = "airbnb.csv.gz"
data = pd.read_csv(
        path,
        delimiter = ";",
        nrows=100000,  # approx. 10% of data
        names=[
            "city",
            "country",          
            "latitude",
            "longitude",
            "roomType",
            "price",
            "N_reviews",
            "review",
        ],  # specify names directly since they don't change
        skiprows=1,  # don't read header since names specified directly
        usecols=[0,1,2,3,4,5,6, 7],)
data['N_reviews'].fillna(0)
data = data.dropna()
data.to_csv("airbnb.csv",index=False)