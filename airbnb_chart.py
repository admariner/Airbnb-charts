# -*- coding: utf-8 -*-
# Copyright 2018-2022 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""An example of showing geographic data."""

import os

import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.express as px

# SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON
st.set_page_config(layout="wide", page_title="Airbnb Demo", page_icon=":house:")

# LOAD DATA ONCE
@st.cache_resource
def load_data():
    path = "airbnb-listings.csv"
#     if not os.path.isfile(path):
#         path = f"https://github.com/streamlit/demo-uber-nyc-pickups/raw/main/{path}"

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
        usecols=[38,44,45,46,48,56,72, 81],  # doesn't load last column, constant value "B02512"
        # parse_dates=[
        #     "date/time"
        # ],  # set as datetime instead of converting after the fact
    )
    data['N_reviews'].fillna(0)
    data = data.dropna()
    print(data.info())
    return data


# FUNCTION FOR Locations MAPS
def map(data, lat, lon, zoom):
    st.write(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude": lat,
                "longitude": lon,
                "zoom": zoom,
                "pitch": 50,
            },
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    data=data,
                    get_position=["longitude", "latitude"],
                    radius=100,
                    elevation_scale=4,
                    elevation_range=[0, 1000],
                    pickable=True,
                    extruded=True,
                ),
            ],
        )
    )


# FILTER DATA FOR A SPECIFIC price, CACHE
@st.cache_data
def filterdata(df, price):
    return df[df["price"] <= price]


# FILTER DATA FOR A SPECIFIC price, CACHE
@st.cache_data
def filterdatapie(df, price):
    filtered = df[df["price"] <= price]
    nrows =filtered.shape[0]
    countries ,hist = np.unique(filtered["city"], return_counts=True)
    indx= hist> nrows *0.01
    print(indx)
    hist = hist[indx]
    countries =countries[indx]
    return pd.DataFrame({ "N_acomodation": hist, "city": countries})

# # FILTER DATA BY price
@st.cache_data
def histdata(df, price):
    filtered = data[df["price"] <= price]
    hist = np.histogram(filtered["price"], bins=30, range=(0, 600))[0]
    return pd.DataFrame({"price": range(0,600,20), "ac ": hist})

@st.cache_data
def dist(df,price):
    df=df[df["price"]>=price]
    roomType = np.unique(df["roomType"])
    dist_room =[]
    for r in roomType:
        dist_room.append(df[df['roomType']  == r]['review'])
    return dist_room,roomType 
@st.cache_data
def dist2(df,price):
    df=df[df["price"]>=price]
    return  df[["review","N_reviews","roomType"]]


# FILTER DATA BY HOUR
#@st.cache_data
#def histdata(df, price):
#    filtered = df[df["price"] <= price]
#    hist = np.histogram(filtered["price"], bins=30, range=(0, 600))[0]
#    return pd.DataFrame({"price": range(0,600,20), "accomodation": hist})


# STREAMLIT APP LAYOUT
data = load_data()
#row1_1, row1_2= st.columns((2, 2))

#with row1_2:

st.title("Airbnb Data")
st.write(""" 
         The Airbnb listings is a non-commercial dataset,  that allows individuals to explore about  Airbnb usage in multiple cities around the world.  
         The Airbnb listings dataset provides key attributes to analyze how Airbnb is being used to compete in the housing market.
         Here we focus in: 📊 Data Analysis and 📈 Data Visualization

         Let's start with a friendly, easy-to-understand chart. Here, cities and countries are showcased using hierarchical rectangles. The size of these rectangles corresponds to the number 
         of Airbnb listings, and their colors give you a quick look at average prices by city.
""")

df=data.groupby(['country', 'city']).agg(listings=pd.NamedAgg(column='price', aggfunc='count'),average_price=pd.NamedAgg(column='price', aggfunc='mean')).reset_index()
print(df.columns)
#df = data.groupby(['country', 'city']).size().reset_index(name='listings')
#df['average_price'] = data.groupby(['country', 'city'])['price'].transform('mean')
#df = df.drop_duplicates(subset=['country', 'city']).reset_index(drop=True)

fig = px.treemap(df, path=[px.Constant('world'), 'country', 'city'], values='listings', color='average_price')
st.plotly_chart(fig, theme=None, use_container_width=True)
#st.write("")
with st.expander("City listings and prices Tree Map "):
    st.write(""" The chart reveals that the top cities with the most listings are Los Angeles, London, Paris, Madrid and Barcelona. When it comes to average listing prices, cities located in Denmark and Hong Kong lead the way as the more expensive options""")

#tab1, tab2 = st.tabs([":moneybag: Price", ":earth_americas: Coutry"])
#with tab1:
st.header("Analysis by price")
st.markdown("Explore Airbnb listings filtered by price. By sliding the slider to the right, you can see the charts update to show your desired price range.")
row2_1,  row2_2, row2_3 = st.columns(3)
with row2_1:
    st.write("")
with row2_2: 
    if not st.session_state.get("url_synced", False):
        try:
            price = int(st.experimental_get_query_params()["price"][0])
            st.session_state["price"] = price
            st.session_state["url_synced"] = True
        except KeyError:
            pass
    # IF THE SLIDER CHANGES, UPDATE THE QUERY PARAM
    def update_query_params():
        price = st.session_state["price"]
        st.experimental_set_query_params(price=price)
    
    st.subheader("Price Picker")
    price = st.slider("", 0, 600, key="price", on_change=update_query_params)
with row2_3:
    st.write("")
row3_1, row3_2= st.columns((1, 2))
with row3_1:
    with st.expander("City Pie Chart"):
        st.write("The chart illustrates the percentage of listings in each city, filtered by a price limit of ", price)
with row3_2:
    df = filterdatapie(data, price)
    fig = px.pie(df, values='N_acomodation', names='city')
    fig.update_traces(textposition='inside')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    st.plotly_chart(fig, theme=None, use_container_width=True)
    top_two_cities = df.nlargest(2, 'N_acomodation')['city'].tolist()
    
st.subheader(':blue[Map Airbnb listing abundance in top two cities]', divider='rainbow')
row4_1, row4_2= st.columns((1, 1))
# get locations
city1_values= data.loc[data['city'] == top_two_cities[0]].iloc[0]
city2_values= data.loc[data['city'] == top_two_cities[1]].iloc[0]
zoom_level = 11
with row4_1:
    st.write(top_two_cities[0])
    map(filterdata(data, price), city1_values['latitude'], city1_values['longitude'], zoom_level)
with row4_2:
    st.write(top_two_cities[1])
    map(filterdata(data, price), city2_values['latitude'], city2_values['longitude'], zoom_level)

st.subheader(':blue[Analysis by Accomodation Type and Reviews filtered by price]', divider='rainbow')
row5_1, row5_2 = st.columns((1, 3))
with row5_1:
    value_counts = data['roomType'].value_counts().reset_index()
    value_counts.columns = ['roomType', 'count']
    fig = px.bar(value_counts, x="count", y="roomType", orientation='h', color = 'roomType', template="simple_white")
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Type of Accomodation Bar Chart"):
        st.write("""Airbnb hosts have a range of options, from listing entire homes/apartments to private and shared rooms.
             However, the nature of the listing and how it's used can vary. Some Airbnb rentals are similar to hotels, potentially causing disruptions for neighbors, impacting housing availability, and possibly even being against the law""")
with row5_2:
    df = dist2(data,price)
    fig = px.scatter(df, x="N_reviews", y="review", color="roomType", marginal_y="violin",
               marginal_x="box", trendline="ols", template="simple_white")
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Average Review x Number of Reviews by type of Accomodation  Chart"):
        st.write("""Airbnb hosts have a range of options, from listing entire homes/apartments to private and shared rooms.
             We can see that most of the listings have few reviews. Most of them are positive for all types of accommodations.""")

#with tab2:
#    st.header("Analysis by country")