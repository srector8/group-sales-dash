# -*- coding: utf-8 -*-
"""GroupSalesDash.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1I2G_yg98NEYHSxSBktFfqnF5LS-CvyFo
"""

import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Group Sales Dashboard")
st.sidebar.title("Group Sales Dashboard")

@st.cache(allow_output_mutation=True)
def load_data(file_path):
    try:
        # Read CSV with Latin-1 encoding
        df = pd.read_csv(file_path, encoding='latin1')
    except UnicodeDecodeError as e:
        st.error(f"Error reading the file: {e}")
        return None
    
    if 'add_datetime' in df.columns:
        df['add_datetime'] = pd.to_datetime(df['add_datetime'])
    
    return df

# Specify your CSV file path
data_file = 'group_sales.csv'

# Load data and convert to UTF-8
data = load_data(data_file)

if data is None:
    st.error("Failed to load data. Please check the file and try again.")
else:
    st.write("Data has been successfully loaded.")

    try:
        data.to_csv('group_sales_utf8.csv', index=False, encoding='utf-8')
    except Exception as e:
        st.error(f"Error saving data: {e}")

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
    page = st.sidebar.selectbox('Select Page', ['Sales by Game', 'Sales Rep Performance', 'Cumulative Stats for Games', 'Cumulative Stats for Reps'])

    if page == 'Sales by Game':
        # Sidebar for event selection
        event_name = st.sidebar.selectbox('Select Event', sorted(data['event_name_display'].unique()))
        
        # Filter data based on selected event
        filtered_data = data[data['event_name_display'] == event_name]
        
        # Calculate days until each event date relative to the current date
        filtered_data['days_until_event'] = (filtered_data['add_datetime'].dt.date - pd.Timestamp.today().date()).dt.days
        
        # Aggregate data by days until event
        aggregated_data = filtered_data.groupby('days_until_event').agg({
            'block_full_price': 'sum',
            'acct_id': 'nunique',
            'num_seats': 'sum'
        }).reset_index()
        
        # Calculate cumulative sums
        aggregated_data['cumulative_sales'] = aggregated_data['block_full_price'].cumsum()
        aggregated_data['cumulative_orders'] = aggregated_data['acct_id'].cumsum()
        aggregated_data['cumulative_tickets_sold'] = aggregated_data['num_seats'].cumsum()
        
        # Average totals for each day count
        average_totals = aggregated_data.groupby('days_until_event').mean().reset_index()
        
        # Plotting using Altair
        chart_sales = alt.Chart(average_totals).mark_line().encode(
            x='days_until_event:Q',
            y='cumulative_sales:Q',
            tooltip=['days_until_event:Q', 'cumulative_sales:Q']
        ).properties(
            title=f'Average Cumulative Sales Over Days Until Event: {event_name}',
            width=800,
            height=300
        )
        
        chart_orders = alt.Chart(average_totals).mark_line(color='orange').encode(
            x='days_until_event:Q',
            y='cumulative_orders:Q',
            tooltip=['days_until_event:Q', 'cumulative_orders:Q']
        ).properties(
            title=f'Average Cumulative Orders Over Days Until Event: {event_name}',
            width=800,
            height=300
        )
        
        chart_tickets = alt.Chart(average_totals).mark_line(color='green').encode(
            x='days_until_event:Q',
            y='cumulative_tickets_sold:Q',
            tooltip=['days_until_event:Q', 'cumulative_tickets_sold:Q']
        ).properties(
            title=f'Average Cumulative Tickets Sold Over Days Until Event: {event_name}',
            width=800,
            height=300
        )
        
        # Display the charts
        st.altair_chart(chart_sales, use_container_width=True)
        st.altair_chart(chart_orders, use_container_width=True)
        st.altair_chart(chart_tickets, use_container_width=True)

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
            rep_time_series_sales.columns = ['Date', 'Total Sales']  

            # Total orders per day
            rep_time_series_orders = filtered_rep_data.groupby(filtered_rep_data['add_datetime'].dt.date)['acct_id'].nunique().reset_index(name='total_orders')
            rep_time_series_orders.columns = ['Date', 'Total Orders']  

            # Total tickets sold per day
            rep_time_series_tickets = filtered_rep_data.groupby(filtered_rep_data['add_datetime'].dt.date)['num_seats'].sum().reset_index()
            rep_time_series_tickets.columns = ['Date', 'Total Tickets Sold']  

            # Time-series line chart using Altair for sales rep total sales
            rep_chart_sales = alt.Chart(rep_time_series_sales).mark_line().encode(
                x='Date:T',  # Rename x-axis
                y=alt.Y('Total Sales:Q', axis=alt.Axis(title='Total Sales')),  
                tooltip=['Date:T', 'Total Sales:Q']
            ).properties(
                title=f'Total Sales Over Time for {sales_rep}',
                width=800,
                height=300
            )

            # Time-series line chart using Altair for sales rep total orders
            rep_chart_orders = alt.Chart(rep_time_series_orders).mark_line(color='orange').encode(
                x='Date:T',  # Rename x-axis
                y=alt.Y('Total Orders:Q', axis=alt.Axis(title='Total Orders')),  
                tooltip=['Date:T', 'Total Orders:Q']
            ).properties(
                title=f'Total Orders Over Time for {sales_rep}',
                width=800,
                height=300
            )

            # Time-series line chart using Altair for sales rep total tickets sold
            rep_chart_tickets = alt.Chart(rep_time_series_tickets).mark_line(color='green').encode(
                x='Date:T',  # Rename x-axis
                y=alt.Y('Total Tickets Sold:Q', axis=alt.Axis(title='Total Tickets Sold')),  
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

    elif page == 'Cumulative Stats for Games':
            # Sidebar for cumulative graphs selection
            game_cumulative_option = st.sidebar.selectbox('Select Cumulative Graph', 
                                                          ['Cumulative Group Sales ($) for Each Game', 
                                                           'Cumulative Group Orders for Each Game', 
                                                           'Cumulative Group Tickets for Each Game'])
        
            # Sort events by their display name using the mapping order
            sorted_events = [event_name_mapping[key] for key in event_name_mapping.keys() if key in data['event_name'].unique()]
        
            if game_cumulative_option == 'Cumulative Group Sales ($) for Each Game':
                # Calculate cumulative sales by game
                cumulative_sales_by_game = data.groupby('event_name_display')['block_full_price'].sum().reset_index()
                cumulative_sales_by_game = cumulative_sales_by_game.sort_values(by='event_name_display', key=lambda x: x.map(lambda name: sorted_events.index(name)))
        
                # Bar chart for cumulative sales by game
                bar_chart_game_sales = alt.Chart(cumulative_sales_by_game).mark_bar().encode(
                    x=alt.X('event_name_display', sort=sorted_events, axis=alt.Axis(title='Game')),
                    y=alt.Y('block_full_price', axis=alt.Axis(title='Cumulative Group Sales ($)')),
                    tooltip=['event_name_display', 'block_full_price']
                ).properties(
                    width=800,
                    height=400
                )
        
                # Display the chart
                st.altair_chart(bar_chart_game_sales, use_container_width=True)
        
                # Table for cumulative sales by game
                st.write("Table for Cumulative Group Sales ($) for Each Game")
                cumulative_sales_by_game.columns = ['Event', 'Total Sales ($)']
                st.write(cumulative_sales_by_game)
        
            elif game_cumulative_option == 'Cumulative Group Orders for Each Game':
                # Group by event and count unique acct_id values
                unique_orders = data.groupby('event_name_display')['acct_id'].nunique().reset_index(name='total_orders')
                unique_orders = unique_orders.sort_values(by='event_name_display', key=lambda x: x.map(lambda name: sorted_events.index(name)))
            
                # Bar chart for cumulative orders by game
                bar_chart_game_orders = alt.Chart(unique_orders).mark_bar().encode(
                    x=alt.X('event_name_display', sort=sorted_events, axis=alt.Axis(title='Game')),
                    y=alt.Y('total_orders', axis=alt.Axis(title='Cumulative Group Orders')),
                    tooltip=['event_name_display', 'total_orders']
                ).properties(
                    width=800,
                    height=400
                )
            
                # Display the chart
                st.altair_chart(bar_chart_game_orders, use_container_width=True)
            
                # Table for cumulative orders by game
                st.write("Table for Cumulative Group Orders for Each Game")
                unique_orders.columns = ['Event', 'Total Orders']
                st.write(unique_orders)



            elif game_cumulative_option == 'Cumulative Group Tickets for Each Game':
                # Calculate cumulative tickets sold by game
                cumulative_tickets_by_game = data.groupby('event_name_display')['num_seats'].sum().reset_index()
                cumulative_tickets_by_game = cumulative_tickets_by_game.sort_values(by='event_name_display', key=lambda x: x.map(lambda name: sorted_events.index(name)))
        
                # Bar chart for cumulative tickets sold by game
                bar_chart_game_tickets = alt.Chart(cumulative_tickets_by_game).mark_bar().encode(
                    x=alt.X('event_name_display', sort=sorted_events, axis=alt.Axis(title='Game')),
                    y=alt.Y('num_seats', axis=alt.Axis(title='Cumulative Group Tickets')),
                    tooltip=['event_name_display', 'num_seats']
                ).properties(
                    width=800,
                    height=400
                )
        
                # Display the chart
                st.altair_chart(bar_chart_game_tickets, use_container_width=True)
        
                # Table for cumulative tickets sold by game
                st.write("Table for Cumulative Group Tickets for Each Game")
                cumulative_tickets_by_game.columns = ['Event', 'Total Tickets']
                st.write(cumulative_tickets_by_game)
    
    elif page == 'Cumulative Stats for Reps':
        # Filter representatives with at least 30 orders
        reps_with_enough_orders = data['acct_rep_full_name'].value_counts()[data['acct_rep_full_name'].value_counts() >= 30].index.tolist()
    
        # Sidebar for cumulative graphs selection
        cumulative_option = st.sidebar.selectbox('Select Cumulative Graph', 
                                                 ['Cumulative Group Sales ($) by Rep', 
                                                  'Cumulative Group Ticket Orders by Rep', 
                                                  'Cumulative Group Tickets Sold by Rep',
                                                'Sales Distribution by Rep for Each Game'])
    
        if cumulative_option == 'Cumulative Group Sales ($) by Rep':
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

            st.write("Table for Cumulative Group Sales ($) by Rep")
            cumulative_sales_by_rep.columns = ['Sales Representative', 'Total Sales ($)']
            st.write(cumulative_sales_by_rep)
    
        elif cumulative_option == 'Cumulative Group Ticket Orders by Rep':
            # Calculate cumulative ticket orders by sales rep
            unique_orders_by_rep = data.groupby('acct_rep_full_name')['acct_id'].nunique().reset_index(name='total_orders')
        
            # Filter out reps with enough orders if needed
            unique_orders_by_rep = unique_orders_by_rep[unique_orders_by_rep['acct_rep_full_name'].isin(reps_with_enough_orders)]
        
            # Sort by total orders descending
            unique_orders_by_rep = unique_orders_by_rep.sort_values(by='total_orders', ascending=False)
        
            # Bar chart for cumulative ticket orders by rep
            bar_chart_orders = alt.Chart(unique_orders_by_rep).mark_bar().encode(
                x=alt.X('acct_rep_full_name', sort='-y', axis=alt.Axis(title='Sales Representative')),
                y=alt.Y('total_orders', axis=alt.Axis(title='Cumulative Ticket Orders')),
                tooltip=['acct_rep_full_name', 'total_orders']
            ).properties(
                width=800,
                height=400
            )
        
            # Display the chart
            st.altair_chart(bar_chart_orders, use_container_width=True)
        
            # Table for cumulative ticket orders by rep
            st.write("Table for Cumulative Group Ticket Orders by Rep")
            unique_orders_by_rep.columns = ['Sales Representative', 'Total Orders']
            st.write(unique_orders_by_rep)


    
        elif cumulative_option == 'Cumulative Group Tickets Sold by Rep':
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

            st.write("Table for Cumulative Group Tickets Sold by Rep")
            cumulative_tickets_sold_by_rep.columns = ['Sales Representative', 'Total Tickets Sold']
            st.write(cumulative_tickets_sold_by_rep)        

        elif cumulative_option == 'Sales Distribution by Rep for Each Game':
            # Filter out representatives with fewer than 30 orders
            reps_with_enough_orders = data['acct_rep_full_name'].value_counts()[data['acct_rep_full_name'].value_counts() >= 30].index.tolist()
        
            # Prepare data for sales distribution by rep for each game
            sales_distribution = data[data['acct_rep_full_name'].isin(reps_with_enough_orders)]
            sales_distribution = sales_distribution.groupby(['event_name_display', 'acct_rep_full_name'])['block_full_price'].sum().reset_index()
        
            # Calculate percentage of sales for each rep for each game
            sales_distribution['sales_percentage'] = sales_distribution.groupby('event_name_display')['block_full_price'].transform(lambda x: (x / x.sum()) * 100)
        
            # Bar chart for sales distribution by rep for each game
            bar_chart_sales_dist = alt.Chart(sales_distribution).mark_bar().encode(
                x=alt.X('event_name_display:N', axis=alt.Axis(title='Game')),
                y=alt.Y('sales_percentage:Q', stack='normalize', axis=alt.Axis(format='%'), title='Sales Percentage'),
                color=alt.Color('acct_rep_full_name:N', legend=alt.Legend(title='Account Rep')),
                order=alt.Order('sales_percentage:Q', sort='descending'),
                tooltip=['event_name_display:N', 'acct_rep_full_name:N', 'block_full_price:Q', 'sales_percentage:Q']
            ).properties(
                width=800,
                height=400
            )
        
            # Display the chart
            st.altair_chart(bar_chart_sales_dist, use_container_width=True)

            # Find the top salesman for each game
            top_salesman_per_game = sales_distribution.loc[sales_distribution.groupby('event_name_display')['block_full_price'].idxmax()]
            
            # Create a DataFrame for the table
            top_salesman_table = top_salesman_per_game[['event_name_display', 'acct_rep_full_name']]
            top_salesman_table.columns = ['Game', 'Top Rep']
            
            # Display the table
            st.table(top_salesman_table)
