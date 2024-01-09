import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pandas import DataFrame
from sqlalchemy import text, exc


def get_query1_fig(query1_df):
    # Create the bar plot
    fig = go.Figure(data=[
        go.Bar(name='Total Planned Sales', x=query1_df['plan_descr'], y=query1_df['total_planned_sales']),
        go.Bar(name='Total Forecast', x=query1_df['plan_descr'], y=query1_df['total_forecast'])
    ])

    # Update the layout
    fig.update_layout(
        height = 500, 
        width = 700,
        barmode='group',
        title='Planned Sales vs Forecast by Plan plot',
        xaxis_title='Plan Description',
        yaxis_title='Values',
    )

    return fig

def get_query2_fig(plan, query2_df):

    query2_plan_df = query2_df[query2_df['plan_descr'] == plan]

    # Create the bar plot
    fig = go.Figure(data=[
        go.Bar(name='Total Planned Sales', x=query2_plan_df['cluster_descr'], y=query2_plan_df['total_planned_sales']),
        go.Bar(name='Total Forecast', x=query2_plan_df['cluster_descr'], y=query2_plan_df['total_forecast'])
    ])

    # Update the layout
    fig.update_layout(
        height = 500, 
        width = 700,
        barmode='group',
        title=f'Planned Sales vs Forecast by Cluster for {plan} plot',
        xaxis_title='Cluster Description',
        yaxis_title='Values'
    )

    return fig, query2_plan_df

def get_query3_fig(plan, query3_df):
    query3_plan_df = query3_df[query3_df['plan_descr'] == plan]
    # Create the bar plot
    fig = go.Figure(data=[
        go.Bar(name='Total Planned Sales', x=query3_plan_df['cluster_descr'], y=query3_plan_df['total_planned_sales']),
        go.Bar(name='Total Sales', x=query3_plan_df['cluster_descr'], y=query3_plan_df['total_sales'])
    ])

    # Update the layout
    fig.update_layout(
        height = 500, 
        width = 750,
        barmode='group',
        title=f'Planned Sales vs Last Year Sales by Cluster for {plan} plot',
        xaxis_title='Cluster Description',
        yaxis_title='Values'
    )

    return fig, query3_plan_df

def get_query4_fig(query4_df):
    item = query4_df['s_item_id']
    # fig = go.Figure(data=[go.Pie(labels=query4_df['cluster_descr'], values=query4_df['max_growth'], 
    #                          text=query4_df['s_item_id'], textinfo='label+text+percent',
    #                          insidetextorientation='radial')])

    # # Update layout
    # fig.update_layout(title='Proportional Growth by Cluster')

    fig = go.Figure(data=[go.Bar(
    x=query4_df['cluster_descr'],
    y=query4_df['max_growth'],
    text=query4_df['s_item_id'],
    textposition='auto',
    marker_color=['#9467bd', '#e377c2', '#7f7f7f']
    )])

    # Update layout
    fig.update_layout(
        title='Top Growth Item Year-on-Year in Each Cluster',
        xaxis_title='Cluster',
        yaxis_title='Max Growth',
        
    )

    # # Update the layout
    # fig.update_layout(  
    #     height = 500, 
    #     width = 700,
    #     barmode='group',
    #     title='Question 2: Planned Sales vs Forecast by Plan',
    #     xaxis_title='Plan Description',
    #     yaxis_title='Values'
    # )

    return fig

def streamlit_main(query1_df, query2_df, query3_df, query4_df):
    st.set_page_config(
        page_title = 'Kivos-Dashboard',
        page_icon = ':bar_chart:',
        layout = 'wide'
    )

    st.title('Query results presentation')

    # st.markdown(
    #     """
    #     The different files and what they represent:
    #     """
    # )

    query1_fig = get_query1_fig(query1_df)

    # col1, col2 = st.columns(2)
    # col1 = st.columns(1)
    # with col1:
    # Plot query 1 figure
    st.subheader("Question 2: Planned Sales vs Forecast by Plan")
    st.plotly_chart(query1_fig, use_container_width=False)
    st.info(
        """
        Resulting dataframe of Planned Sales vs Forecast by Plan Query
        """
    )

    st.dataframe(query1_df)

    # with col2:
        
    # Unique values for plan_descr and cluster_descr
    plans = query1_df['plan_descr'].unique()
    plan = st.selectbox(
        'Please select the plan you wish to see the data for',
        set(plans)
    )

    query2_fig, query2_plandf = get_query2_fig(plan, query2_df)
    query3_fig, query3_plandf = get_query3_fig(plan, query3_df)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader(f'Question 3: Planned Sales vs Forecast by Cluster for {plan}')
        # Plot query 2 figure
        st.plotly_chart(query2_fig, use_container_width=True)
        st.info(
            f"""
            Resulting dataframe of Planned Sales vs Forecast by Cluster Query for {plan} 
            """
        )

        st.dataframe(query2_plandf)

    with col4:
        st.subheader(f'Question 4: Planned Sales vs Last Year Sales by Cluster for {plan}')
        # Plot query 3 figure
        st.plotly_chart(query3_fig, use_container_width=True)
        st.info(
            f"""
            Resulting dataframe of Planned Sales vs Forecast by Cluster Query for {plan} 
            """
        )

        st.dataframe(query3_plandf)

    query4_fig = get_query4_fig(query4_df)
    query4_df.s_item_id = query4_df.s_item_id.astype(str)
    st.subheader("Question 5: Items with largest YoY growth for each cluster")
    # Plot query 4 df
    # st.info(
    #     """
    #     Growth is defined as Total Planned Sales - Total Sales
    #     """
    # )
    st.plotly_chart(query4_fig, use_container_width=False)
    st.info(
        """
        Resulting dataframe of Items with largest YoY growth for each cluster / Growth is defined as Total Planned Sales - Total Sales
        """
    )

    st.dataframe(query4_df)
