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
def load_data(file_path, encoding):
    try:
        df = pd.read_csv(file_path, encoding=encoding)
    except UnicodeDecodeError as e:
        st.error(f"Error reading the file: {e}")
        return None
    
    df['add_datetime'] = pd.to_datetime(df['add_datetime'])
    return df

data_file = 'group_sales.csv'

# Try different encodings based on your knowledge or inspection
encodings_to_try = ['utf-8', 'latin1', 'iso-8859-1', 'utf-16']

data = None
for encoding in encodings_to_try:
    data = load_data(data_file, encoding)
    if data is not None:
        break

if data is None:
    st.error("Failed to load data. Please check the file encoding and try again.")
else:
    # Sidebar for event selection
    event_name = st.sidebar.selectbox('Select Event', data['event_name'].unique())

    # Filter data based on selected event
    filtered_data = data[data['event_name'] == event_name]

    # Prepare data for time-series plots
    # Total sales over time
    time_series_sales = filtered_data.groupby(filtered_data['add_datetime'].dt.date)['block_full_price'].sum().reset_index()
    time_series_sales.columns = ['date', 'total_sales']

    # Total orders per day
    time_series_orders = filtered_data.groupby(filtered_data['add_datetime'].dt.date).size().reset_index(name='total_orders')
    time_series_orders.columns = ['date', 'total_orders']

    # Total tickets sold per day
    time_series_tickets = filtered_data.groupby(filtered_data['add_datetime'].dt.date)['num_seats'].sum().reset_index()
    time_series_tickets.columns = ['date', 'total_tickets']

    # Time-series line chart using Altair for total sales
    chart_sales = alt.Chart(time_series_sales).mark_line().encode(
        x='date:T',
        y='total_sales:Q',
        tooltip=['date:T', 'total_sales:Q']
    ).properties(
        title=f'Total Sales Over Time for Event: {event_name}',
        width=800,
        height=300
    )

    # Time-series line chart using Altair for total orders
    chart_orders = alt.Chart(time_series_orders).mark_line(color='orange').encode(
        x='date:T',
        y='total_orders:Q',
        tooltip=['date:T', 'total_orders:Q']
    ).properties(
        title=f'Total Orders Over Time for Event: {event_name}',
        width=800,
        height=300
    )

    # Time-series line chart using Altair for total tickets sold
    chart_tickets = alt.Chart(time_series_tickets).mark_line(color='green').encode(
        x='date:T',
        y='total_tickets:Q',
        tooltip=['date:T', 'total_tickets:Q']
    ).properties(
        title=f'Total Tickets Sold Over Time for Event: {event_name}',
        width=800,
        height=300
    )

    # Display the charts
    st.altair_chart(chart_sales, use_container_width=True)
    st.altair_chart(chart_orders, use_container_width=True)
    st.altair_chart(chart_tickets, use_container_width=True)
