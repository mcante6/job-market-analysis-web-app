# Job Market Analysis Web App

## Overview
https://jobmarket.streamlit.app/
This project provides a dynamic and interactive way to visualize the IT job market in the USA, focusing on data collected from Dice.com. Born out of the frustration of navigating through outdated job market information online, this web app aims to offer up-to-date insights into the demand for various IT skills, job types, and the availability of positions across different locations.

## Access the Web App

Explore the IT job market in real-time by visiting the web app at [Job Market Analysis](https://jobmarket.streamlit.app/).

The web app is developed using Streamlit and showcases data collected through a sophisticated web scraping mechanism. The collected data is stored in an SQLite database, allowing for efficient data management and retrieval. This approach enables users to explore the IT job market with current and relevant data, aiding job seekers, recruiters, and market analysts in making informed decisions.

## Motivation

The motivation behind this project stems from the challenge of finding accurate and current job market information. Traditional job search methods often lead to outdated or irrelevant data, making it difficult for job seekers to understand the current market trends and for employers to identify the actual demand for specific skills. This project aims to bridge this gap by providing a real-time overview of the job market, specifically tailored to the IT sector in the USA.

## Features

- **Data Collection:** Utilizes Selenium for web scraping to collect job market data from Dice.com, focusing on job types, skills, and locations within the USA. The system is designed to collect data for the last 5 days, ensuring up-to-date information while maintaining historical data in the SQL database for trend analysis.
- **Database Management:** Employs SQLite to store and manage the scraped data efficiently, ensuring data integrity and quick access.
- **Interactive Web App:** Built with Streamlit, the web app offers a user-friendly interface for dynamic data visualization, including:
  - Top 10 skills by location.
  - Total jobs by skill.
  - Total jobs by location.
  - Remote job skills.
  - Historical job market trends.
- **Updated Information:** Features a mechanism to fetch and display the last update date, ensuring users have access to the most recent data.
- **Customizable Analysis:** Users can choose between different data sources (e.g., Dice or LinkedIn data) and select specific locations or skills for a personalized analysis.

## Technologies Used

- **Python:** For web scraping, data manipulation, and web app development.
- **Selenium:** Automated web browser interaction for data scraping.
- **SQLite:** Database for storing and querying job market data.
- **Streamlit:** Framework for creating the interactive web app.
- **Pandas:** Data analysis and manipulation.
- **Matplotlib:** Data visualization.

## How to Use

1. **Setup Environment:** Ensure Python is installed and set up a virtual environment.
2. **Install Dependencies:** Install required Python packages using `pip install -r requirements.txt`.
3. **Run the Scraper:** Execute the scraper script to collect data from Dice.com and store it in the SQLite database.
4. **Launch the Web App:** Run `streamlit run webapp.py` to start the web app.
5. **Explore Data:** Use the web app's sidebar to select data sources, locations, and analysis types to view different visualizations of the job market.

## Project Structure

- `scraper.py`: Script for web scraping job data.
- `database.py`: Handles database operations.
- `webapp.py`: Streamlit web app for data visualization.
- `requirements.txt`: Lists all the Python packages required for the project.

## Contributing

Contributions to enhance this project are welcome. Please follow the standard fork and pull request workflow.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to Dice.com for serving as a primary data source.
- Streamlit community for providing an excellent tool for rapid web app development.
