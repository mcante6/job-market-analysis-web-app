# UPADATED VERSION WORKING 2.0 - Collecting data from LinkedIn and Dice /// HEADLESS 


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from urllib.parse import quote_plus
from time import sleep
import sqlite3
from datetime import datetime
import re
import random
from concurrent.futures import ThreadPoolExecutor, as_completed


# Linkedin Constants for CSS and XPath selectors
CSS_SELECTOR = '#main > div.scaffold-layout__list-detail-inner > div.scaffold-layout__list > header > div.jobs-search-results-list__title-heading > small > div > span'
XPATH_SELECTOR = '/html/body/div[1]/div/main/div/h1/span[1]'
XPATH_SELECTOR_2 = '/html/body/div[5]/div[3]/div[4]/div/div/main/div[2]/div[1]/header/div[1]/small/div/span'

# DICe Constants for CSS and XPath selectors
DICE_CSS_SELECTOR = '#totalJobCount'
DICE_XPATH_SELECTOR = '/html/body/dhi-js-dice-client/div/dhi-search-page-container/dhi-search-page/div/dhi-search-page-results/div/div[3]/div/dhi-filters-widget/div/section[1]/div[1]/span'

#job search options
LOCATIONS = ['California, United States', 'North Carolina, United States', 'Florida, United States', 'Colorado, United States', 'Washington, United States', 'Washington DC-Baltimore Area', 'New York, United States', 'Texas, United States', 'Boston, United States', 'New Jersey, United States']
SKILLS = ["Big Data", "Web Developer", "Android", "IOS Developer", "C++", "Data Quality" ,"QA Tester", "Java", "Frontend developer", "backend developer","Data Scientist", "Machine Learning", "AI Engineer", "Business Intelligence", "Data Analyst", "Data Engineer", "Deep Learning", "Software Developer", "Data Visualization", "MLOps", "BI", "SQL", "Sagemaker", "Cloud", "AWS", "Azure", "GCP", "Python", "TensorFlow", "PyTorch", "Salesforce Admin", "Databriks", "Snowflake", "help desk","devops", "system analyst", "IT support"] # Add all the skills here
JOB_TYPES = ['Remote', 'Office', 'Hybrid']
GEO_ID_MAP = {'California, United States': '1234567', 'North Carolina, United States': '101915197', 'Florida, United States' : '101318387', 'Colorado, United States': '105763813', 'Washington, United States' : '103977389', 'Washington DC-Baltimore Area' : '90000097', 'New York, United States' : '105080838', 'Texas, United States': '102748797', 'Boston, United States': '102380872', 'New Jersey, United States': '101651951'} # Map locations to their geoIds
# FOR TESTING
# LOCATIONS = ['North Carolina, United States', 'Washington DC-Baltimore Area', 'New York, United States', 'Washington, United States','California, United States']
# SKILLS = ["Data Scientist", "Help Desk", "Data Analyst", "Software Developer", "Sagemaker", "Salesforce", "Machine Learning"]

# Create table if it does not exist
def initialize_database(conn):
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS dice_job_market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_date DATE NOT NULL,
            location TEXT NOT NULL,
            job_type TEXT NOT NULL,
            skill TEXT NOT NULL,
            total_jobs INTEGER,
            is_remote BOOLEAN DEFAULT FALSE
        );
        CREATE TABLE IF NOT EXISTS updated_dice_job_market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_date DATE NOT NULL,
            location TEXT NOT NULL,
            job_type TEXT NOT NULL,
            skill TEXT NOT NULL,
            total_jobs INTEGER,
            is_remote BOOLEAN DEFAULT FALSE
        );
    ''')
    conn.commit()

# def setup_driver():  # NORMAL
#     # Setup Chrome WebDriver
#     service = Service(ChromeDriverManager().install())
#     options = webdriver.ChromeOptions()
#     # Add any required options here (e.g., headless mode)
#     driver = webdriver.Chrome(service=service, options=options)
#     return driver

def setup_driver():  # HEADLESS
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run Chrome in headless mode
    options.add_argument('--no-sandbox')  # Bypass OS security model, required on Linux if running as root
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    options.add_argument('window-size=1920x1080')
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    return driver


conn = sqlite3.connect('jobs.db')
cursor = conn.cursor()
driver = setup_driver()
c = conn.cursor()
try:
    initialize_database(conn)
except sqlite3.OperationalError as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")





def has_recent_data_dice(location, skill, cursor):
    """
    Check if there's recent data for a given location and skill on Dice, 
    ignoring the job type.
    """
    query = """
    SELECT EXISTS(
        SELECT 1 
        FROM dice_job_market_data 
        WHERE location = ? AND skill = ? AND 
              collection_date > datetime('now', '-5 day')
    )
    """
    cursor.execute(query, (location, skill))
    return cursor.fetchone()[0]

def random_delay(min_seconds, max_seconds):
    sleep(random.uniform(min_seconds, max_seconds))


# Initialize counters and sets for summary
total_jobs_collected = 0
skills_collected = set()
locations_collected = set()
failure_counter = 0  # Initialize the failure counter


#######   DICE   ########
def collect_from_dice(driver, conn, cursor):
    # Iterate over all locations for non-remote jobs
    for location in LOCATIONS:
        for skill in SKILLS:
            if not has_recent_data_dice(location, skill, cursor):
                search_url = construct_dice_url(skill, location, is_remote=False)
                job_count = find_dice_job_count(driver, search_url)
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Insert data for location-based search
                cursor.execute('''INSERT INTO dice_job_market_data (collection_date, location, job_type, skill, total_jobs, jobs_less_than_10_applicants) VALUES (?, ?, ?, ?, ?, ?)''', (now, location, "Office", skill, job_count, 0))  # "N/A" is used for job_type since it's not a distinguishing factor on Dice
                conn.commit()
            else:
                print(f"Recent data already exists for {skill} in {location}. Skipping.")

    # Collect for remote jobs across the USA
    for skill in SKILLS:
        if not has_recent_data_dice("Remote", skill, cursor):
            search_url = construct_dice_url(skill, "USA", is_remote=True)
            job_count = find_dice_job_count(driver, search_url)
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Insert data for remote search
            cursor.execute('''INSERT INTO dice_job_market_data (collection_date, location, job_type, skill, total_jobs, jobs_less_than_10_applicants) VALUES (?, ?, ?, ?, ?, ?)''', (now, "Remote", "Remote", skill, job_count, 0))
            conn.commit()
        else:
            print(f"Recent data already exists for {skill} in Remote. Skipping.")

    print("Data collection from Dice completed.")
    update_latest_data_table(conn, 'dice')

def construct_dice_url(SKILL, LOCATIONS, is_remote=False):
    base_url = "https://www.dice.com/jobs"
    skill_query = quote_plus(SKILL)
    location_query = quote_plus(LOCATIONS) if not is_remote else "USA"
    job_type_filter = "&filters.isRemote=true" if is_remote else ""
    query_filters = "NOT (%22Ph.D%22 OR %22Phd%22 OR %22Master degree%22 OR %22Senior%22 OR %22Sr%22 OR %22Director%22 OR %22VP%22 OR %22Manager%22 OR %22Lead%22 OR %22Principal%22 OR %22Graduate%22 OR %22Tutor%22 OR %22Instructor%22 OR %22citizenship%22 OR %22Experienced%22)"
    full_url = f"{base_url}?q={skill_query} {query_filters}&location={location_query}&countryCode=US&radius=30&radiusUnit=mi&page=1&pageSize=20&filters.postedDate=SEVEN{job_type_filter}&language=en"
    return full_url

def find_dice_job_count(driver, search_url):
    driver.get(search_url)
    sleep(5)  # Adjust based on your needs
    try:
        job_count_element = driver.find_element(By.CSS_SELECTOR, DICE_CSS_SELECTOR)
        job_count = int(job_count_element.text.replace(',', ''))
        return job_count
    except (TimeoutException, WebDriverException) as e:
        print(f"Error finding job count on Dice: {e}")
        return 0

# Function to update the latest data table
def update_latest_data_table(conn, source):
    cursor = conn.cursor()
    
    if source == 'linkedin':
        # Delete existing records in updated_job_market_data table for LinkedIn
        cursor.execute('DELETE FROM updated_job_market_data')
        
        # Insert the latest LinkedIn records into updated_job_market_data table
        cursor.execute('''
            INSERT INTO updated_job_market_data (collection_date, location, job_type, skill, total_jobs, jobs_less_than_10_applicants)
            SELECT MAX(jmd.collection_date) as collection_date, jmd.location, jmd.job_type, jmd.skill, jmd.total_jobs, jmd.jobs_less_than_10_applicants
            FROM job_market_data jmd
            GROUP BY jmd.location, jmd.job_type, jmd.skill
            ORDER BY jmd.collection_date DESC
        ''')

    elif source == 'dice':
        # Delete existing records in updated_dice_job_market_data table for Dice
        cursor.execute('DELETE FROM updated_dice_job_market_data')
        
        # Insert the latest Dice records into updated_dice_job_market_data table
        cursor.execute('''
            INSERT INTO updated_dice_job_market_data (collection_date, location, job_type, skill, total_jobs, jobs_less_than_10_applicants)
            SELECT MAX(djmd.collection_date) as collection_date, djmd.location, djmd.job_type, djmd.skill, djmd.total_jobs, djmd.jobs_less_than_10_applicants
            FROM dice_job_market_data djmd
            GROUP BY djmd.location, djmd.job_type, djmd.skill
            ORDER BY djmd.collection_date DESC
        ''')

    conn.commit()



collect_from_dice(driver, conn, cursor)

# Ensure to close the connection when done
conn.close()
driver.quit()

# Print summary
print(f"Total jobs collected: {total_jobs_collected}")
print(f"Total unique skills collected: {len(skills_collected)}")
print(f"Total unique locations collected: {len(locations_collected)}")
print(f"Total failures encountered: {failure_counter}")