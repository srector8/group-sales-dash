# -*- coding: utf-8 -*-
"""GroupSalesDash.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1I2G_yg98NEYHSxSBktFfqnF5LS-CvyFo
"""

import streamlit as st
import pandas as pd
import altair as alt

# Set the title of the Streamlit page
st.set_page_config(page_title="Group Sales Dashboard")

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

# Specify your CSV file path
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
    # Define mapping for event_name
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

    # Page selection
    page = st.sidebar.selectbox('Select Page', ['Sales by Game', 'Sales Rep Performance', 'Cumulative Stats for Reps'])

    if page == 'Sales by Game':
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
            x='Date:T',  # Rename x-axis
            y=alt.Y('Total Sales:Q', axis=alt.Axis(title='Total Sales')),  # Rename y-axis and set title
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
        if not time_series_sales.empty:
            total_sales = time_series_sales['Total Sales'].sum()
            st.info(f"{event_name} has reached ${total_sales:.2f} in total group sales over all time.")
            
        st.altair_chart(chart_orders, use_container_width=True)
        if not time_series_orders.empty:
            total_orders = time_series_orders['Total Orders'].sum()
            st.info(f"{event_name} has accumulated {total_orders} total group orders over all time.")
            
        st.altair_chart(chart_tickets, use_container_width=True)
        if not time_series_tickets.empty:
            total_tickets = time_series_tickets['Total Tickets Sold'].sum()
            st.info(f"{event_name} has sold {total_tickets} total group tickets over all time.")

    elif page == 'Sales Rep Performance':
        # Filter representatives with at least 30 rows
        reps_with_enough_rows = data['acct_rep_full_name'].value_counts()[data['acct_rep_full_name'].value_counts() >= 30].index.tolist()

        # Sidebar for sales rep selection
        sales_rep = st.sidebar.selectbox('Select Sales Representative', sorted(reps_with_enough_rows))

        # Filter data based on selected sales rep
        filtered_rep_data = data[data['acct_rep_full_name'] == sales_rep]

        if filtered_rep_data.empty:
            st.warning(f"No data available for {sales_rep}. Please select another sales representative.")
        else:
            # Prepare data for sales rep performance charts
            # Total sales over time
            rep_time_series_sales = filtered_rep_data.groupby(filtered_rep_data['add_datetime'].dt.date)['block_full_price'].sum().reset_index()
            rep_time_series_sales.columns = ['Date', 'Total Sales']  # Rename columns for Altair

            # Total orders per day
            rep_time_series_orders = filtered_rep_data.groupby(filtered_rep_data['add_datetime'].dt.date).size().reset_index(name='total_orders')
            rep_time_series_orders.columns = ['Date', 'Total Orders']  # Rename columns for Altair

            # Total tickets sold per day
            rep_time_series_tickets = filtered_rep_data.groupby(filtered_rep_data['add_datetime'].dt.date)['num_seats'].sum().reset_index()
            rep_time_series_tickets.columns = ['Date', 'Total Tickets Sold']  # Rename columns for Altair

            # Time-series line chart using Altair for sales rep total sales
            rep_chart_sales = alt.Chart(rep_time_series_sales).mark_line().encode(
                x='Date:T',  # Rename x-axis
                y=alt.Y('Total Sales:Q', axis=alt.Axis(title='Total Sales')),  # Rename y-axis and set title
                tooltip=['Date:T', 'Total Sales:Q']
            ).properties(
                title=f'Total Sales Over Time for {sales_rep}',
                width=800,
                height=300
            )

            # Time-series line chart using Altair for sales rep total orders
            rep_chart_orders = alt.Chart(rep_time_series_orders).mark_line(color='orange').encode(
                x='Date:T',  # Rename x-axis
                y=alt.Y('Total Orders:Q', axis=alt.Axis(title='Total Orders')),  # Rename y-axis and set title
                tooltip=['Date:T', 'Total Orders:Q']
            ).properties(
                title=f'Total Orders Over Time for {sales_rep}',
                width=800,
                height=300
            )

            # Time-series line chart using Altair for sales rep total tickets sold
            rep_chart_tickets = alt.Chart(rep_time_series_tickets).mark_line(color='green').encode(
                x='Date:T',  # Rename x-axis
                y=alt.Y('Total Tickets Sold:Q', axis=alt.Axis(title='Total Tickets Sold')),  # Rename y-axis and set title
                tooltip=['Date:T', 'Total Tickets Sold:Q']
            ).properties(
                title=f'Total Tickets Sold Over Time for {sales_rep}',
                width=800,
                height=300
            )

            # Display the charts with appropriate labels
            st.altair_chart(rep_chart_sales, use_container_width=True)
            if not rep_time_series_sales.empty:
                total_rep_sales = rep_time_series_sales['Total Sales'].sum()
                st.info(f"{sales_rep} has reached ${total_rep_sales:.2f} in total group sales over this time.")
            
            st.altair_chart(rep_chart_orders, use_container_width=True)
            if not rep_time_series_orders.empty:
                total_rep_orders = rep_time_series_orders['Total Orders'].sum()
                st.info(f"{sales_rep} has accumulated {total_rep_orders} total group orders over this time.")
                
            st.altair_chart(rep_chart_tickets, use_container_width=True)
            if not rep_time_series_tickets.empty:
                total_rep_tickets = rep_time_series_tickets['Total Tickets Sold'].sum()
                st.info(f"{sales_rep} has sold {total_rep_tickets} total group tickets over this time.")

    elif page == 'Cumulative Stats for Reps':
        # Filter representatives with at least 30 orders
        reps_with_enough_orders = data['acct_rep_full_name'].value_counts()[data['acct_rep_full_name'].value_counts() >= 30].index.tolist()
    
        # Sidebar for cumulative graphs selection
        cumulative_option = st.sidebar.selectbox('Select Cumulative Graph', 
                                                 ['Cumulative Sales ($) by Rep', 
                                                  'Cumulative Ticket Orders by Rep', 
                                                  'Cumulative Tickets Sold by Rep',
                                                'Sales Distribution by Rep for Each Game'])
    
        if cumulative_option == 'Cumulative Sales ($) by Rep':
            # Calculate cumulative sales by sales rep
            cumulative_sales_by_rep = data.groupby('acct_rep_full_name')['block_full_price'].sum().reset_index()
            cumulative_sales_by_rep = cumulative_sales_by_rep[cumulative_sales_by_rep['acct_rep_full_name'].isin(reps_with_enough_orders)]
            cumulative_sales_by_rep = cumulative_sales_by_rep.sort_values(by='block_full_price', ascending=False)
    
            # Bar chart for cumulative sales by rep
            bar_chart_sales = alt.Chart(cumulative_sales_by_rep).mark_bar().encode(
                x=alt.X('acct_rep_full_name', sort='-y', axis=alt.Axis(title='Sales Representative')),
                y=alt.Y('block_full_price', axis=alt.Axis(title='Cumulative Sales ($)')),
                tooltip=['acct_rep_full_name', 'block_full_price']
            ).properties(
                width=800,
                height=400
            )
    
            # Display the chart
            st.altair_chart(bar_chart_sales, use_container_width=True)
    
        elif cumulative_option == 'Cumulative Ticket Orders by Rep':
            # Calculate cumulative ticket orders by sales rep
            cumulative_orders_by_rep = data.groupby('acct_rep_full_name').size().reset_index(name='total_orders')
            cumulative_orders_by_rep = cumulative_orders_by_rep[cumulative_orders_by_rep['acct_rep_full_name'].isin(reps_with_enough_orders)]
            cumulative_orders_by_rep = cumulative_orders_by_rep.sort_values(by='total_orders', ascending=False)
    
            # Bar chart for cumulative ticket orders by rep
            bar_chart_orders = alt.Chart(cumulative_orders_by_rep).mark_bar().encode(
                x=alt.X('acct_rep_full_name', sort='-y', axis=alt.Axis(title='Sales Representative')),
                y=alt.Y('total_orders', axis=alt.Axis(title='Cumulative Ticket Orders')),
                tooltip=['acct_rep_full_name', 'total_orders']
            ).properties(
                width=800,
                height=400
            )
    
            # Display the chart
            st.altair_chart(bar_chart_orders, use_container_width=True)
    
        elif cumulative_option == 'Cumulative Tickets Sold by Rep':
            # Calculate cumulative tickets sold by sales rep
            cumulative_tickets_sold_by_rep = data.groupby('acct_rep_full_name')['num_seats'].sum().reset_index()
            cumulative_tickets_sold_by_rep = cumulative_tickets_sold_by_rep[cumulative_tickets_sold_by_rep['acct_rep_full_name'].isin(reps_with_enough_orders)]
            cumulative_tickets_sold_by_rep = cumulative_tickets_sold_by_rep.sort_values(by='num_seats', ascending=False)
    
            # Bar chart for cumulative tickets sold by rep
            bar_chart_tickets = alt.Chart(cumulative_tickets_sold_by_rep).mark_bar().encode(
                x=alt.X('acct_rep_full_name', sort='-y', axis=alt.Axis(title='Sales Representative')),
                y=alt.Y('num_seats', axis=alt.Axis(title='Cumulative Tickets Sold')),
                tooltip=['acct_rep_full_name', 'num_seats']
            ).properties(
                width=800,
                height=400
            )
    
            # Display the chart
            st.altair_chart(bar_chart_tickets, use_container_width=True)
        elif cumulative_option == 'Sales Distribution by Rep for Each Game':
            # Prepare data for sales distribution by rep for each game
            sales_distribution = data.groupby(['event_name_display', 'acct_rep_full_name'])['block_full_price'].sum().reset_index()
        
            # Calculate percentage of sales for each rep for each game
            sales_distribution['block_full_price'] = pd.to_numeric(sales_distribution['block_full_price'], errors='coerce')

            sales_distribution['sales_percentage'] = sales_distribution.groupby('event_name_display')['block_full_price'].apply(lambda x: (x / x.sum() * 100) if x.sum() != 0 else 0)

        
            # Bar chart for sales distribution by rep for each game
            bar_chart_sales_dist = alt.Chart(sales_distribution).mark_bar().encode(
                x=alt.X('event_name_display', axis=alt.Axis(title='Game')),
                y=alt.Y('sales_percentage:Q', stack='normalize', axis=alt.Axis(format='%'), title='Sales Percentage'),
                color='acct_rep_full_name:N',
                tooltip=['event_name_display', 'acct_rep_full_name', 'block_full_price', 'sales_percentage']
            ).properties(
                width=800,
                height=400,
                title='Sales Distribution by Rep for Each Game'
            )
        
            # Display the chart
            st.altair_chart(bar_chart_sales_dist, use_container_width=True)
