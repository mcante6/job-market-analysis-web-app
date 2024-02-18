import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# Database connection function
def get_connection():
    return sqlite3.connect('jobs.db')

# Function to load data
def load_data(table_name):
    conn = get_connection()
    df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
    conn.close()
    return df

# Function to display top 10 skills by location
def display_top_skills_by_location(df, location):
    filtered_df = df[df['location'] == location]
    skill_counts = filtered_df.groupby('skill')['total_jobs'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(skill_counts)

# Function to display total jobs by skill
def display_total_jobs_by_skill(df):
    skill_jobs = df.groupby('skill')['total_jobs'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(skill_jobs)

# Function to display total jobs by location
def display_total_jobs_by_location(df):
    location_jobs = df.groupby('location')['total_jobs'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(location_jobs)

# Function to display remote job skills
def display_remote_job_skills(df):
    remote_df = df[df['job_type'] == 'Remote']
    remote_skill_counts = remote_df.groupby('skill')['total_jobs'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(remote_skill_counts)

# Function to fetch the last update date
def get_last_update_date(source='dice'):
    conn = get_connection()
    if source == 'dice':
        query = 'SELECT MAX(collection_date) FROM dice_job_market_data'
    else:
        query = 'SELECT MAX(collection_date) FROM job_market_data'
    last_update_date = pd.read_sql(query, conn).iloc[0,0]
    conn.close()
    return last_update_date

# Main app structure
def main():
    st.title('Job Market Analysis')

    # Selection of data table
    table_name = st.sidebar.selectbox('Select Table', ['dice_job_market_data', 'updated_dice_job_market_data'])

    # Display the last update date based on the selected table
    last_update_date = get_last_update_date(table_name)
    st.write(f"Last updated on: {last_update_date}")

    # Load data based on the selected table
    df = load_data(table_name)

    # Selection for different analyses
    analysis_type = st.sidebar.radio("Select Analysis Type", 
                                     ['Top 10 Skills by Location', 'Total Jobs by Skill', 'Total Jobs by Location', 'Remote Job Skills'])


    if analysis_type == 'Top 10 Skills by Location':
        location = st.sidebar.selectbox('Select Location', pd.unique(df['location']))
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

    # Additional visualizations and data views can be added here

if __name__ == '__main__':
    main()
