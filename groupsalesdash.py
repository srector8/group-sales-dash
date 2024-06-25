# -*- coding: utf-8 -*-
"""GroupSalesDash.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1I2G_yg98NEYHSxSBktFfqnF5LS-CvyFo
"""

import streamlit as st
import pandas as pd
import altair as alt

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

encodings_to_try = ['utf-8', 'latin1', 'iso-8859-1', 'utf-16']

data = None
for encoding in encodings_to_try:
    data = load_data(data_file, encoding)
    if data is not None:
        break

if data is None:
    st.error("Failed to load data. Please check the file encoding and try again.")
else:
    # Mapping event_name values to display values
    event_name_mapping = {
        'E240509': '5/9 v.s. Liberty',
        'E240514L': '5/14 v.s. Fever',
        'E240517': '5/17 v.s. Mystic',
        'E240523': '5/23 v.s. Lynx',
        'E240528L': '5/28 v.s. Mercury',
        'E240531L': '5/31 v.s. Wings',
        'E240604L': '6/4 v.s. Mystics',
        'E240608L': '6/8 v.s. Liberty',
        'E240610L': '6/10 v.s. Fever',
        'E240618': '6/18 v.s. Sparks',
        'E240628': '6/28 v.s. Dream',
        'E240707': '7/7 v.s. Dream',
        'E240710': '7/10 v.s. Liberty',
        'E240714': '7/14 v.s. Mercury',
        'E240823L': '8/23 v.s. Sky',
        'E240901L': '9/1 v.s. Storm',
        'E240903': '9/3 v.s. Storm',
        'E240906L': '9/6 v.s. Aces',
        'E240917L': '9/17 v.s. Lynx',
        'E240919L': '9/19 v.s. Sky'
    }

    # Replace event_name with mapped values
    data['event_name_display'] = data['event_name'].map(event_name_mapping).fillna(data['event_name'])

    # Sidebar for event selection
    event_name = st.sidebar.selectbox('Select Event', sorted(data['event_name_display'].unique()))

    # Filter data based on selected event
    filtered_data = data[data['event_name_display'] == event_name]

    # Prepare data for time-series plots
    # Total sales over time
    time_series_sales = filtered_data.groupby(filtered_data['add_datetime'].dt.date)['block_full_price'].sum().reset_index()
    time_series_sales.columns = ['Date', 'Total Sales']  # Rename columns for Altair

    # Total orders per day
    time_series_orders = filtered_data.groupby(filtered_data['add_datetime'].dt.date).size().reset_index(name='total_orders')
    time_series_orders.columns = ['Date', 'Total Orders']  # Rename columns for Altair

    # Total tickets sold per day
    time_series_tickets = filtered_data.groupby(filtered_data['add_datetime'].dt.date)['num_seats'].sum().reset_index()
    time_series_tickets.columns = ['Date', 'Total Tickets Sold']  # Rename columns for Altair

    # Time-series line chart using Altair for total sales
    chart_sales = alt.Chart(time_series_sales).mark_line().encode(
        x='Date:T',  
        y=alt.Y('Total Sales:Q', axis=alt.Axis(title='Total Sales')),  
        tooltip=['Date:T', 'Total Sales:Q']
    ).properties(
        title=f'Total Sales Over Time for Event: {event_name}',
        width=800,
        height=300
    )

    # Time-series line chart using Altair for total orders
    chart_orders = alt.Chart(time_series_orders).mark_line(color='orange').encode(
        x='Date:T',  # Rename x-axis
        y=alt.Y('Total Orders:Q', axis=alt.Axis(title='Total Orders')),  # Rename y-axis and set title
        tooltip=['Date:T', 'Total Orders:Q']
    ).properties(
        title=f'Total Orders Over Time for Event: {event_name}',
        width=800,
        height=300
    )

    # Time-series line chart using Altair for total tickets sold
    chart_tickets = alt.Chart(time_series_tickets).mark_line(color='green').encode(
        x='Date:T',  # Rename x-axis
        y=alt.Y('Total Tickets Sold:Q', axis=alt.Axis(title='Total Tickets Sold')),  # Rename y-axis and set title
        tooltip=['Date:T', 'Total Tickets Sold:Q']
    ).properties(
        title=f'Total Tickets Sold Over Time for Event: {event_name}',
        width=800,
        height=300
    )

    # Display the charts with appropriate labels
    st.altair_chart(chart_sales, use_container_width=True)
    st.altair_chart(chart_orders, use_container_width=True)
    st.altair_chart(chart_tickets, use_container_width=True)
