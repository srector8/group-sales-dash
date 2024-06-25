# -*- coding: utf-8 -*-
"""GroupSalesDash.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1I2G_yg98NEYHSxSBktFfqnF5LS-CvyFo
"""

import streamlit as st
import pandas as pd
import altair as alt

# Load your data
@st.cache_data
def load_data():
    df = pd.read_csv('group_sales.csv')
    df['add_datetime'] = pd.to_datetime(df['add_datetime'])
    return df

data = load_data()

# Sidebar for event selection
event_name = st.sidebar.selectbox('Select Event', data['event_name'].unique())

# Filter data based on selected event
filtered_data = data[data['event_name'] == event_name]

# Prepare data for time-series plot
time_series_data = filtered_data.groupby(filtered_data['add_datetime'].dt.date)['block_full_price'].sum().reset_index()
time_series_data.columns = ['date', 'total_sales']

# Time-series line chart using Altair
chart = alt.Chart(time_series_data).mark_line().encode(
    x='date:T',
    y='total_sales:Q',
    tooltip=['date:T', 'total_sales:Q']
).properties(
    title=f'Total Sales Over Time for Event: {event_name}',
    width=800,
    height=400
)

# Display the chart
st.altair_chart(chart, use_container_width=True)
