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
def load_data(file_path, encoding='utf-8'):
    try:
        df = pd.read_csv(file_path, encoding=encoding)
    except UnicodeDecodeError as e:
        st.error(f"Error reading the file: {e}")
        return None
    
    df['add_datetime'] = pd.to_datetime(df['add_datetime'])
    return df

data_file = 'group_sales.csv'

# Specify the encoding (adjust as needed)
encoding = 'utf-8'

# Load data
data = load_data(data_file, encoding=encoding)

if data is None:
    st.error("Failed to load data. Please check the file encoding and try again.")
else:
    # Sidebar for event selection
    event_name = st.sidebar.selectbox('Select Event', data['event_name'].unique())

    # Filter data based on selected event
    filtered_data = data[data['event_name'] == event_name]

    # Prepare data for time-series plots
    # Total sales per day
    sales_data = filtered_data.groupby(filtered_data['add_datetime'].dt.date)['block_full_price'].sum().reset_index()
    sales_data.columns = ['date', 'total_sales']

    # Total orders per day (counting rows)
    orders_data = filtered_data.groupby(filtered_data['add_datetime'].dt.date).size().reset_index(name='total_orders')
    orders_data.columns = ['date', 'total_orders']

    # Total tickets sold per day (sum of num_seats)
    tickets_data = filtered_data.groupby(filtered_data['add_datetime'].dt.date)['num_seats'].sum().reset_index()
    tickets_data.columns = ['date', 'total_tickets_sold']

    # Time-series line charts using Altair
    chart_sales = alt.Chart(sales_data).mark_line().encode(
        x='date:T',
        y='total_sales:Q',
        tooltip=['date:T', 'total_sales:Q']
    ).properties(
        title=f'Total Sales Over Time for Event: {event_name}',
        width=800,
        height=300
    )

    chart_orders = alt.Chart(orders_data).mark_line().encode(
        x='date:T',
        y='total_orders:Q',
        tooltip=['date:T', 'total_orders:Q']
    ).properties(
        title=f'Total Orders Over Time for Event: {event_name}',
        width=800,
        height=300
    )

    chart_tickets = alt.Chart(tickets_data).mark_line().encode(
        x='date:T',
        y='total_tickets_sold:Q',
        tooltip=['date:T', 'total_tickets_sold:Q']
    ).properties(
        title=f'Total Tickets Sold Over Time for Event: {event_name}',
        width=800,
        height=300
    )

    # Display the charts
    st.altair_chart(chart_sales, use_container_width=True)
    st.altair_chart(chart_orders, use_container_width=True)
    st.altair_chart(chart_tickets, use_container_width=True)
