import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Database connection function
def get_connection():
    return sqlite3.connect('jobs.db')

# Function to load data
def load_data(table_name):
    conn = get_connection()
    df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
    conn.close()
    return df

# New Function to create a histogram of total jobs over time
def display_jobs_over_time(table_name):
    conn = get_connection()
    # Assuming you have a date column in your table to aggregate data by day
    query = f"SELECT collection_date, SUM(total_jobs) as total_jobs FROM {table_name} GROUP BY collection_date"
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Convert collection_date to datetime format for better handling and sorting
    df['collection_date'] = pd.to_datetime(df['collection_date'])
    df.sort_values('collection_date', inplace=True)
    
    # Create the histogram
    fig = px.bar(df, x='collection_date', y='total_jobs', title='Total Jobs Over Time')
    fig.update_xaxes(categoryorder='category ascending')  # Ensure the dates are in ascending order
    st.plotly_chart(fig)

# Enhanced Dynamic Bubble Map Visualization
def display_dynamic_bubble_map(df):
    # User selection for the type of bubble map
    bubble_map_type = st.sidebar.radio("Bubble Map Type", ['By Location', 'By Skill'])

    if bubble_map_type == 'By Location':
        # Calculate total jobs for each location and sort them in descending order
        location_totals = df.groupby('location')['total_jobs'].sum().reset_index().sort_values('total_jobs', ascending=False)
        # User selects a location from the sorted list
        location_options = location_totals['location'].unique()
        location = st.sidebar.selectbox('Select Location', options=location_options)
        # Filter data for the selected location
        df_filtered = df[df['location'] == location]
        # Prepare data for the bubble map by location: Get top 10 skills based on total jobs
        skills_data = df_filtered.groupby('skill')['total_jobs'].sum().nlargest(10).reset_index()
        fig = px.scatter(skills_data, x='skill', y='total_jobs', size='total_jobs', color='skill',
                         hover_name='skill', hover_data=['total_jobs'],
                         title=f'Top 10 Skills in {location}')
        st.plotly_chart(fig)

    elif bubble_map_type == 'By Skill':
        # Calculate total jobs for each skill and sort them in descending order
        skill_totals = df.groupby('skill')['total_jobs'].sum().reset_index().sort_values('total_jobs', ascending=False)
        # User selects a skill from the sorted list
        skill_options = skill_totals['skill'].unique()
        skill = st.sidebar.selectbox('Select Skill', options=skill_options)
        # Filter data for the selected skill
        df_filtered = df[df['skill'] == skill]
        # Prepare data for the bubble map by skills: Include all locations
        location_data = df_filtered.groupby('location')['total_jobs'].sum().reset_index()
        fig = px.scatter(location_data, x='location', y='total_jobs', size='total_jobs', color='location',
                         hover_name='location', hover_data=['total_jobs'],
                         title=f'Jobs for "{skill}" Across Locations')
        st.plotly_chart(fig)



# Improved Function to display top 10 skills by location with Plotly
def display_top_skills_by_location(df, location):
    filtered_df = df[df['location'] == location]
    skill_counts = filtered_df.groupby('skill')['total_jobs'].sum().sort_values(ascending=False).head(10)
    fig = px.bar(skill_counts, y=skill_counts.values, x=skill_counts.index, text=skill_counts.values,
                 labels={'x':'Skill', 'y':'Total Jobs'}, title=f'Top 10 Skills in {location}')
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', xaxis_tickangle=-45)
    st.plotly_chart(fig)

# Function to display jobs by skill across all locations
def display_jobs_by_skill(df, selected_skill):
    filtered_df = df[df['skill'] == selected_skill]
    jobs_by_location = filtered_df.groupby('location')['total_jobs'].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(jobs_by_location, x='location', y='total_jobs', text='total_jobs',
                 labels={'location': 'Location', 'total_jobs': 'Total Jobs'},
                 title=f'Total Jobs for "{selected_skill}" by Location')
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(xaxis={'categoryorder':'total descending'}, xaxis_tickangle=-45)
    st.plotly_chart(fig)

# Function to display total jobs by skill with Plotly
def display_total_jobs_by_skill(df):
    skill_jobs = df.groupby('skill')['total_jobs'].sum().sort_values(ascending=False).head(10)
    fig = px.bar(skill_jobs, y=skill_jobs.values, x=skill_jobs.index, text=skill_jobs.values,
                 labels={'x':'Skill', 'y':'Total Jobs'}, title='Total Jobs by Skill')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

# Function to display total jobs by location with Plotly
def display_total_jobs_by_location(df):
    location_jobs = df.groupby('location')['total_jobs'].sum().sort_values(ascending=False).head(10)
    fig = px.bar(location_jobs, y=location_jobs.values, x=location_jobs.index, text=location_jobs.values,
                 labels={'x':'Location', 'y':'Total Jobs'}, title='Total Jobs by Location')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

# Function to display remote job skills with Plotly
def display_remote_job_skills(df):
    remote_df = df[df['job_type'] == 'Remote']
    remote_skill_counts = remote_df.groupby('skill')['total_jobs'].sum().sort_values(ascending=False).head(10)
    fig = px.bar(remote_skill_counts, y=remote_skill_counts.values, x=remote_skill_counts.index, text=remote_skill_counts.values,
                 labels={'x':'Skill', 'y':'Total Jobs'}, title='Remote Job Skills')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

# Function to fetch the last update date
def get_last_update_date(table_name):
    conn = get_connection()
    query = f'SELECT MAX(collection_date) FROM {table_name}'
    last_update_date = pd.read_sql(query, conn).iloc[0,0]
    conn.close()
    return last_update_date

# Main app structure
def main():
    st.title('Job Market Analysis')

    # UI improvements
    table_name = 'updated_dice_job_market_data'
    last_update_date = get_last_update_date(table_name)
    st.sidebar.markdown(f"**Last updated on:** {last_update_date}")
    st.markdown(f"Data reflects job openings from the last 7 days as of {last_update_date}.")


    df = load_data(table_name)

    analysis_type = st.sidebar.radio(
        "Select Analysis Type",
        ['Bubble Map','Top 10 Skills by Location', 'Jobs by Skill Across Locations', 'Total Jobs by Skill', 'Total Jobs by Location', 'Remote Job Skills', 'Jobs Over Time'],
        key='analysis_type'
    )

    if analysis_type == 'Top 10 Skills by Location':
        location = st.sidebar.selectbox('Select Location', pd.unique(df['location']), key='location')
        st.header(f'Top 10 Skills in {location}')
        display_top_skills_by_location(df, location)
    elif analysis_type == 'Total Jobs by Skill':
        st.header('Total Jobs by Skill')
        display_total_jobs_by_skill(df)
    elif analysis_type == 'Total Jobs by Location':
        st.header('Total Jobs by Location')
        display_total_jobs_by_location(df)
    elif analysis_type == 'Remote Job Skills':
        st.header('Remote Job Skills')
        display_remote_job_skills(df)
    elif analysis_type == 'Bubble Map':
        st.header('Dynamic Bubble Map Visualization')
        display_dynamic_bubble_map(df)
    elif analysis_type == 'Jobs Over Time':
        st.header('Total Jobs Over Time')
        display_jobs_over_time(table_name)  # Call the new function
    elif analysis_type == 'Jobs by Skill Across Locations':
        # Aggregate total jobs for each skill and sort them in descending order
        skills_total_jobs = df.groupby('skill')['total_jobs'].sum().sort_values(ascending=False).reset_index()
        skills_sorted = skills_total_jobs['skill'].tolist()  # Convert to list for the dropdown

        skill = st.sidebar.selectbox('Select Skill', options=skills_sorted, key='skill')
        st.header(f'Jobs for "{skill}" Across Locations')
        display_jobs_by_skill(df, skill)

if __name__ == '__main__':
    main()
